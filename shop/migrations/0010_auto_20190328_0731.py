# Generated by Django 2.1.5 on 2019-03-28 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_auto_20190328_0731'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='files',
            field=models.ManyToManyField(blank=True, to='shop.FileGallery'),
        ),
        migrations.AddField(
            model_name='product',
            name='image_gallery',
            field=models.ManyToManyField(blank=True, to='shop.ImageGallery'),
        ),
    ]
