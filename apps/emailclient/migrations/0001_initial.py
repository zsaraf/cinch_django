# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PendingEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('category', models.IntegerField()),
                ('tag', models.CharField(max_length=75)),
                ('template_name', models.CharField(max_length=75)),
                ('merge_vars', models.TextField(null=True, blank=True)),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'pending_emails',
                'managed': False,
            },
        ),
    ]
