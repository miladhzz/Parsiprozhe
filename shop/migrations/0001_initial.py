# Generated by Django 2.1.5 on 2019-03-29 19:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import shop.helper


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(allow_unicode=True, max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=500, null=True)),
                ('parentCategory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.Category', verbose_name='Parent Category')),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=200)),
                ('mobile', models.CharField(blank=True, max_length=11)),
                ('message', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FileGallery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('file', models.FileField(upload_to='media/upload/files')),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name_plural': 'File Gallery',
                'verbose_name': 'File Gallery',
            },
        ),
        migrations.CreateModel(
            name='ImageGallery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('pic', models.ImageField(default='upload/images/no-img.jpg', upload_to='upload/images')),
                ('alt', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name_plural': 'Image Gallery',
                'verbose_name': 'Image Gallery',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('family', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=200)),
                ('mobile', models.CharField(max_length=11)),
                ('address', models.TextField(blank=True, max_length=500)),
                ('order_note', models.CharField(blank=True, max_length=200)),
                ('payment_type', models.IntegerField(choices=[(1, 'At place'), (2, 'Online')], default=2)),
                ('is_accept_agreement', models.BooleanField()),
                ('order_status', models.IntegerField(choices=[(1, 'Completed'), (2, 'Canceled'), (3, 'In progress'), (4, 'Checking'), (5, 'Paymentting')], default=4)),
                ('payment_tool', models.CharField(max_length=100)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('order_update_date', models.DateTimeField(blank=True, null=True)),
                ('count_of_allow_download', models.IntegerField(default=10)),
                ('date_of_expire_download', models.DateTimeField(blank=True, null=True)),
                ('random_order_id', models.IntegerField(default=shop.helper.random_int, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='shop.Order')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('payment_code', models.CharField(max_length=200, unique=True)),
                ('bank_tracking_code', models.CharField(blank=True, max_length=200)),
                ('Payment_status', models.IntegerField(choices=[(1, 'Initial'), (2, 'To Bank'), (3, 'From Bank'), (4, 'Error'), (5, 'Complete')], default=1)),
                ('message', models.CharField(blank=True, max_length=200)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='shop.Order')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(allow_unicode=True, max_length=100, unique=True)),
                ('content', models.TextField(max_length=2000)),
                ('publish_date', models.DateTimeField(auto_now_add=True)),
                ('is_active_comment', models.BooleanField(default=False)),
                ('status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Published'), (3, 'Reopen')], default=1)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('has_discount', models.BooleanField(default=False)),
                ('super_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True)),
                ('type_of_product', models.IntegerField(choices=[(1, 'Download'), (2, 'Postal')], default=1)),
                ('transportation_class', models.IntegerField(blank=True, choices=[(1, 'Express Post'), (2, 'Normal Post'), (3, 'Tiepaks')], null=True)),
                ('available_in_stock', models.IntegerField(choices=[(1, 'Available'), (2, 'Unavailable'), (3, 'In Prebuy')], default=1)),
                ('pic', models.ImageField(default='upload/images/no-img.jpg', upload_to='upload/product/images')),
                ('summary', models.CharField(blank=True, max_length=100)),
                ('count_of_download', models.IntegerField(null=True)),
                ('category', models.ManyToManyField(blank=True, to='shop.Category')),
                ('files', models.ManyToManyField(blank=True, to='shop.FileGallery')),
                ('image_gallery', models.ManyToManyField(blank=True, to='shop.ImageGallery')),
                ('related_product', models.ManyToManyField(blank=True, related_name='_product_related_product_+', to='shop.Product', verbose_name='Related Product')),
            ],
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(allow_unicode=True, unique=True)),
                ('description', models.TextField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(blank=True, to='shop.Tag'),
        ),
        migrations.AddField(
            model_name='product',
            name='writer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Product'),
        ),
        migrations.AddField(
            model_name='city',
            name='province',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Province'),
        ),
    ]
