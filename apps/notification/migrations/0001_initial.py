# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(max_length=25)),
                ('title', models.CharField(max_length=250, null=True, blank=True)),
                ('message', models.CharField(max_length=250, null=True, blank=True)),
                ('pn_message', models.CharField(max_length=250, null=True, blank=True)),
                ('is_silent', models.IntegerField()),
                ('priority', models.IntegerField()),
            ],
            options={
                'db_table': 'notification_types',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OpenNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('data', models.TextField(null=True, blank=True)),
                ('notification_type_id', models.IntegerField()),
                ('notification_vars', models.TextField(null=True, blank=True)),
                ('has_sent', models.IntegerField()),
                ('send_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'open_notifications',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PastNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('data', models.TextField(null=True, blank=True)),
                ('notification_type_id', models.IntegerField()),
                ('notification_vars', models.TextField(null=True, blank=True)),
                ('has_sent', models.IntegerField()),
                ('send_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'past_notifications',
                'managed': False,
            },
        ),
    ]
