# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_variation'),
    ]

    operations = [
        migrations.AddField(
            model_name='variation',
            name='product',
            field=models.ForeignKey(default=1, to='products.Product'),
            preserve_default=False,
        ),
    ]
