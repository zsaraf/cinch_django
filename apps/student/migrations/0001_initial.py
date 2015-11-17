# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('student_id', models.IntegerField(null=True, blank=True)),
                ('tutor_id', models.IntegerField(null=True, blank=True)),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'favorites',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('credits', models.DecimalField(max_digits=19, decimal_places=4)),
            ],
            options={
                'db_table': 'students',
                'managed': False,
            },
        ),
    ]
