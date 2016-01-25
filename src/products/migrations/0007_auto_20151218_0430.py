# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_auto_20151217_2108'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductFeatured',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('image', models.ImageField(upload_to=products.models.image_upload_to_featured)),
                ('title', models.CharField(blank=True, null=True, max_length=120)),
                ('text', models.CharField(blank=True, null=True, max_length=220)),
                ('text_right', models.BooleanField(default=False)),
                ('text_css_color', models.CharField(blank=True, null=True, max_length=6)),
                ('show_price', models.BooleanField(default=False)),
                ('make_image_background', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('product', models.ForeignKey(to='products.Product')),
            ],
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories', 'verbose_name': 'Category'},
        ),
        migrations.AlterModelOptions(
            name='productimage',
            options={'verbose_name_plural': 'Product Images', 'verbose_name': 'Product Image'},
        ),
    ]
