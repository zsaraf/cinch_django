# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('token', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=100)),
                ('device_model', models.CharField(max_length=40, null=True, blank=True)),
                ('system_version', models.FloatField(null=True, blank=True)),
                ('app_version', models.FloatField()),
                ('timezone_name', models.CharField(max_length=100, null=True, blank=True)),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'devices',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DoNotEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'do_not_email',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EmailUserData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('received_timeout_credits', models.DateTimeField(null=True, blank=True)),
                ('received_student_cancellation_credits', models.DateTimeField(null=True, blank=True)),
                ('received_tutor_cancellation_credits', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'email_user_data',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PasswordChangeRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField(null=True, blank=True)),
                ('random_hash', models.CharField(max_length=100, null=True, blank=True)),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'password_change_requests',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PastBonus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('amount', models.DecimalField(max_digits=19, decimal_places=4)),
                ('timestamp', models.DateTimeField()),
                ('is_tier_bonus', models.IntegerField()),
            ],
            options={
                'db_table': 'past_bonuses',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=25)),
                ('value', models.DecimalField(max_digits=19, decimal_places=4)),
            ],
            options={
                'db_table': 'promo_codes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SeshState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(max_length=32, null=True, blank=True)),
            ],
            options={
                'db_table': 'sesh_states',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_id', models.CharField(max_length=100)),
                ('issue_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'tokens',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('full_name', models.CharField(max_length=100)),
                ('share_code', models.CharField(max_length=10)),
                ('token_id', models.IntegerField()),
                ('web_token_id', models.IntegerField()),
                ('school_id', models.IntegerField()),
                ('is_verified', models.IntegerField()),
                ('verification_id', models.CharField(max_length=100)),
                ('stripe_customer_id', models.CharField(max_length=32, null=True, blank=True)),
                ('stripe_recipient_id', models.CharField(max_length=32, null=True, blank=True)),
                ('full_legal_name', models.CharField(max_length=100)),
                ('profile_picture', models.CharField(max_length=250)),
                ('major', models.CharField(max_length=100)),
                ('class_year', models.CharField(max_length=25, null=True, blank=True)),
                ('bio', models.CharField(max_length=256)),
                ('sesh_state_id', models.IntegerField()),
                ('salt', models.CharField(max_length=25)),
                ('notifications_enabled', models.IntegerField()),
                ('completed_app_tour', models.IntegerField()),
                ('is_rep', models.IntegerField()),
                ('is_test', models.IntegerField()),
                ('timestamp', models.DateTimeField()),
                ('is_disabled', models.IntegerField()),
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
        ),
    ]
