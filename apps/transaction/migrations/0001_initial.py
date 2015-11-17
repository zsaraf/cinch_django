# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AddedOnlineCredit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('from_email', models.CharField(max_length=100)),
                ('amount', models.DecimalField(max_digits=19, decimal_places=4)),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'added_online_credit',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CashOutAttempt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('amount', models.DecimalField(max_digits=19, decimal_places=4)),
                ('successful', models.IntegerField()),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'cash_out_attempts',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OutstandingCharge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('past_sesh_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('amount_owed', models.DecimalField(max_digits=19, decimal_places=4)),
                ('amount_payed', models.DecimalField(max_digits=19, decimal_places=4)),
                ('resolved', models.IntegerField()),
                ('code', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'outstanding_charges',
                'managed': False,
            },
        ),
    ]
