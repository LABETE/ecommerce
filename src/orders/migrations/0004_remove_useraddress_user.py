# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_useraddress'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useraddress',
            name='user',
        ),
    ]
