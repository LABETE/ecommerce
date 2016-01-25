# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercheckout',
            name='braintree_id',
            field=models.CharField(blank=True, null=True, max_length=120),
        ),
    ]
