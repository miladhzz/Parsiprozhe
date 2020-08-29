from django.shortcuts import render
from django.views import View
from . import forms


class ContactMe(View):
    template_name = 'contact.html'
    form_class = forms.ContactForm
    initial = {'key': 'value'}
    # success_url = '.'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    new_contact = None

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_contact = form.save()
            return render(request, self.template_name, {'form': form,
                                                        'new_contact': new_contact })
