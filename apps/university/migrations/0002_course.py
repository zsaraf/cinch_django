# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('university', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('school_id', models.IntegerField(null=True, blank=True)),
                ('department_id', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('number', models.CharField(max_length=5, null=True, blank=True)),
            ],
            options={
                'db_table': 'classes',
                'managed': False,
            },
        ),
    ]
