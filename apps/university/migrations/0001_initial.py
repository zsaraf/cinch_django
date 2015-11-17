# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BonusPointAllocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('school_id', models.IntegerField()),
                ('sesh_completed_points', models.SmallIntegerField()),
                ('tutor_referral_points', models.SmallIntegerField()),
                ('monthly_point_goal', models.SmallIntegerField(null=True, blank=True)),
                ('max_awards', models.SmallIntegerField()),
                ('start_date', models.DateTimeField(null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('bonus_amount', models.DecimalField(max_digits=19, decimal_places=4)),
            ],
            options={
                'db_table': 'bonus_point_allocation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Class',
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
        migrations.CreateModel(
            name='Constant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('school_id', models.IntegerField()),
                ('free_credits', models.DecimalField(max_digits=19, decimal_places=4)),
                ('hourly_rate', models.DecimalField(max_digits=19, decimal_places=4)),
                ('sesh_comp', models.DecimalField(max_digits=19, decimal_places=4)),
                ('minimum_sesh_duration', models.IntegerField()),
                ('max_bids', models.IntegerField()),
                ('sesh_cancellation_timeout_minutes', models.IntegerField()),
                ('administrative_percentage', models.FloatField()),
                ('additional_student_fee', models.DecimalField(max_digits=19, decimal_places=4)),
                ('late_cancellation_fee', models.IntegerField()),
                ('user_share_amount', models.DecimalField(max_digits=19, decimal_places=4)),
                ('friend_share_amount', models.DecimalField(max_digits=19, decimal_places=4)),
                ('first_tutor_rate', models.DecimalField(max_digits=19, decimal_places=4)),
                ('tutor_min', models.DecimalField(max_digits=19, decimal_places=4)),
                ('instant_request_timeout', models.IntegerField()),
                ('start_time_approaching_reminder', models.IntegerField()),
                ('set_start_time_initial_reminder', models.IntegerField()),
                ('set_start_time_reminder_interval', models.IntegerField()),
                ('android_launch_date', models.DateTimeField()),
                ('tutor_promo_recruiter_award', models.DecimalField(max_digits=19, decimal_places=4)),
                ('tutor_promo_recruitee_award', models.DecimalField(max_digits=19, decimal_places=4)),
                ('cancellation_administrative_percentage', models.DecimalField(max_digits=19, decimal_places=4)),
            ],
            options={
                'db_table': 'constants',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('school_id', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=20, null=True, blank=True)),
                ('abbrev', models.CharField(max_length=10, null=True, blank=True)),
            ],
            options={
                'db_table': 'departments',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credit_amount', models.FloatField()),
                ('one_time_use', models.IntegerField()),
                ('school_id', models.IntegerField()),
                ('exp_date', models.DateTimeField(null=True, blank=True)),
                ('banner_message', models.CharField(max_length=200)),
                ('num_uses', models.IntegerField(null=True, blank=True)),
                ('learn_request_title', models.CharField(max_length=200, null=True, blank=True)),
                ('banner_header', models.CharField(max_length=25, null=True, blank=True)),
            ],
            options={
                'db_table': 'discounts',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DiscountUse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('discount_id', models.IntegerField(null=True, blank=True)),
                ('user_id', models.IntegerField(null=True, blank=True)),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'discount_uses',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('enabled', models.IntegerField()),
                ('email_domain', models.CharField(max_length=100)),
                ('num_tutors', models.IntegerField()),
                ('tutors_needed', models.IntegerField()),
                ('ready_to_add_classes', models.IntegerField()),
                ('requests_enabled', models.IntegerField()),
            ],
            options={
                'db_table': 'schools',
                'managed': False,
            },
        ),
    ]
