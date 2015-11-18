# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20151117_0149'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='device',
            options={'managed': False},
        ),
    ]
