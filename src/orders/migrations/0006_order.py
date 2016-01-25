# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0008_cart_tax_percentage'),
        ('orders', '0005_useraddress_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shipping_total_price', models.DecimalField(default=5.99, decimal_places=2, max_digits=50)),
                ('order_total', models.DecimalField(max_digits=50, decimal_places=2)),
                ('billing_address', models.ForeignKey(to='orders.UserAddress', related_name='billing_address')),
                ('cart', models.ForeignKey(to='carts.Cart')),
                ('shipping_address', models.ForeignKey(to='orders.UserAddress', related_name='shipping_address')),
                ('user', models.ForeignKey(to='orders.UserCheckout')),
            ],
        ),
    ]
