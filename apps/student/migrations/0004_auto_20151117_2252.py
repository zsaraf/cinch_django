# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_auto_20151117_2246'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studentcourse',
            options={'managed': False},
        ),
    ]
