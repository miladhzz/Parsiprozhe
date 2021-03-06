from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    RedirectView
)
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin
from django.utils.encoding import uri_to_iri
from .models import Product, OrderItem, Order, Category
from django.views.generic.base import ContextMixin
from django.views.decorators.http import require_POST
from . import forms
from .cart import Cart
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from zeep import Client
from django.http import HttpResponse, HttpResponseRedirect
from parsiprozhe.settings import MERCHANT
from logger import statistic
from django.contrib import messages


class FormContextMixin(ContextMixin):
    def get_context_data(self, *args, **kwargs):
        ctx = super(FormContextMixin, self).get_context_data(**kwargs)
        ctx['cart_product_from'] = forms.CartAddProductForm()
        return ctx


# TODO cache
class TopSelMixin(ContextMixin):
    def get_context_data(self, *args, **kwargs):
        ctx = super(TopSelMixin, self).get_context_data(**kwargs)
        ctx['top_sel'] = Product.objects.all()[9:12]
        return ctx


# TODO cache
class RecentlyMixin(ContextMixin):
    def get_context_data(self, *args, **kwargs):
        ctx = super(RecentlyMixin, self).get_context_data(**kwargs)
        ctx['recently_view'] = Product.objects.all()[3:9]
        return ctx


class LatestMixin(ContextMixin):
    def get_context_data(self, *args, **kwargs):
        ctx = super(LatestMixin, self).get_context_data(**kwargs)
        ctx['latest_product'] = Product.objects.all().order_by('-id')[0:3]
        return ctx


class ProductList(FormContextMixin, ListView):
    model = Product
    template_name = 'product_list.html'
    paginate_by = 12
    queryset = Product.objects.all()


class ProductDisplay(FormContextMixin, DetailView):
    model = Product
    template_name = 'product_detail.html'

    def get_object(self, **kwargs):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Product, slug=uri_to_iri(slug))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = forms.CommentForm()
        context['comments'] = self.object.comment_set.filter(is_active=True)
        return context


class ProductComment(SingleObjectMixin, FormView):
    template_name = 'product_detail.html'
    form_class = forms.CommentForm
    model = Product

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        new_form = form.save(commit=False)
        new_form.product = self.object
        new_form.save()
        messages.info(self.request, message="نظر شما با موفقیت ثبت شد، در اولین فرصت بررسی میکنیم.")
        return super(ProductComment, self).form_valid(form)

    def get_success_url(self):
        return reverse('product-detail', kwargs={'slug': self.object.slug})

    def get_object(self, **kwargs):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Product, slug=uri_to_iri(slug))


class AuthorDetail(View):

    def get(self, request, *args, **kwargs):
        view = ProductDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ProductComment.as_view()
        return view(request, *args, **kwargs)


class Home(TopSelMixin, RecentlyMixin, LatestMixin, FormContextMixin, ListView):
    model = Product
    template_name = "home.html"


def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = forms.OrderCheckoutForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         count=item['count'])
            # Clear the cart
            cart.clear()
            return redirect('to_bank', order_id=order.random_order_id)

    else:
        form = forms.OrderCheckoutForm()
    return render(request, 'checkout.html', {'cart': cart,
                                             'form': form})


zarinpall_gateway = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'
CallbackURL = 'http://parsiprozhe.ir/callback/'


def to_bank(request, order_id):
    order = get_object_or_404(Order, random_order_id=order_id)
    description = "خرید فایل از پارسی پروژه"  # Required
    email = order.email
    mobile = order.mobile
    order_items = OrderItem.objects.filter(order=order)
    amount = 0
    for item in order_items:
        amount += item.price
    if amount == 0:
        return render(request, 'bank.html', {'order_items': order_items})
    order.amount = amount
    order.save()
    client = Client(zarinpall_gateway)
    result = client.service.PaymentRequest(MERCHANT, amount, description, email, mobile, CallbackURL)
    if result.Status == 100 and len(result.Authority) == 36:
        order.authority = str(result.Authority)
        order.save()
        return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
    else:
        return HttpResponse('Error code: ' + str(result.Status))


def callback(request):
    statistic.log(request)
    if request.GET.get('Status') == 'OK':
        authority = str(request.GET['Authority'])
        order = get_object_or_404(Order, authority=authority)
        client = Client(zarinpall_gateway)
        result = client.service.PaymentVerification(MERCHANT, authority, order.amount)
        if result.Status == 100:
            order_items = OrderItem.objects.filter(order=order)
            order.order_status = 1  # Complete
            order.refId = result.RefID
            order.save()
            return render(request, 'callback.html', {'order_items': order_items,
                                                     'refId': order.refId})
        elif result.Status == 101:
            order_items = OrderItem.objects.filter(order=order)
            return render(request, 'callback.html', {'order_items': order_items,
                                                     'refId': order.refId})
        else:
            return HttpResponse('تراکنش ناموفق.\nStatus: ' + str(result.Status) +
                                '<a href="http://parsiprozhe.ir">بازگشت</a>')
    else:
        return HttpResponse('پرداخت توسط کاربر لغو شد' + '<a href="http://parsiprozhe.ir">بازگشت</a>')


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = forms.CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 count=cd['count'],
                 update_count=cd['update'])
    return redirect('cart_detail')


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = forms.CartUpdateProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 count=cd['count'],
                 update_count=cd['update'])
    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_count_from'] = forms.CartUpdateProductForm(initial={'count': item['count'],
                                                                   'update': True})
    return render(request, 'cart.html', {'cart': cart})


class CategoryProductList(FormContextMixin, ListView):
    model = Product
    template_name = 'category_product_list.html'

    def get_queryset(self):
        print(self.kwargs.get('slug'))
        queryset = Product.objects.filter(category__slug=uri_to_iri(self.kwargs.get('slug')))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        try:
            context["product"] = Category.objects.get(slug=uri_to_iri(self.kwargs.get('slug')))
        except Category.DoesNotExist:
            pass
        return context


class SignUp(CreateView):
    template_name = 'registration/register.html'
    form_class = forms.RegisterForm
    success_url = reverse_lazy('login')


@method_decorator(login_required, name='dispatch')
class LogoutUser(RedirectView):
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return super().get_redirect_url(*args, **kwargs)
