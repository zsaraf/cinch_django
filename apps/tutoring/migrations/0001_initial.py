# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OpenBid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_id', models.IntegerField()),
                ('tutor_id', models.IntegerField()),
                ('timestamp', models.DateTimeField()),
                ('tutor_latitude', models.FloatField(null=True, blank=True)),
                ('tutor_longitude', models.FloatField(null=True, blank=True)),
            ],
            options={
                'db_table': 'open_bids',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OpenRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('student_id', models.IntegerField()),
                ('school_id', models.IntegerField()),
                ('class_id', models.IntegerField()),
                ('description', models.CharField(max_length=100)),
                ('processing', models.IntegerField()),
                ('timestamp', models.DateTimeField()),
                ('est_time', models.IntegerField()),
                ('num_people', models.IntegerField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('hourly_rate', models.DecimalField(max_digits=19, decimal_places=4)),
                ('expiration_time', models.DateTimeField()),
                ('is_instant', models.IntegerField()),
                ('available_blocks', models.TextField()),
                ('location_notes', models.CharField(max_length=32)),
                ('discount_id', models.IntegerField(null=True, blank=True)),
                ('sesh_comp', models.DecimalField(max_digits=19, decimal_places=4)),
            ],
            options={
                'db_table': 'open_requests',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OpenSesh',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('past_request_id', models.IntegerField()),
                ('tutor_id', models.IntegerField()),
                ('timestamp', models.DateTimeField()),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('has_started', models.IntegerField()),
                ('student_id', models.IntegerField()),
                ('tutor_longitude', models.FloatField(null=True, blank=True)),
                ('tutor_latitude', models.FloatField(null=True, blank=True)),
                ('set_time', models.DateTimeField(null=True, blank=True)),
                ('is_instant', models.IntegerField()),
                ('location_notes', models.CharField(max_length=32)),
                ('has_received_start_time_approaching_reminder', models.IntegerField(null=True, blank=True)),
                ('has_received_set_start_time_initial_reminder', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'open_seshes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PastBid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('past_request_id', models.IntegerField()),
                ('tutor_id', models.IntegerField()),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'past_bids',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PastRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('student_id', models.IntegerField()),
                ('class_id', models.IntegerField()),
                ('school_id', models.IntegerField()),
                ('description', models.CharField(max_length=100)),
                ('time', models.DateTimeField()),
                ('num_people', models.IntegerField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('est_time', models.IntegerField()),
                ('status', models.IntegerField()),
                ('hourly_rate', models.DecimalField(max_digits=19, decimal_places=4)),
                ('available_blocks', models.TextField()),
                ('is_instant', models.IntegerField()),
                ('expiration_time', models.DateTimeField()),
                ('has_seen', models.IntegerField()),
                ('discount_id', models.IntegerField(null=True, blank=True)),
                ('cancellation_reason', models.CharField(max_length=30, null=True, blank=True)),
                ('sesh_comp', models.DecimalField(max_digits=19, decimal_places=4)),
            ],
            options={
                'db_table': 'past_requests',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PastSesh',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('past_request_id', models.IntegerField()),
                ('tutor_id', models.IntegerField()),
                ('student_id', models.IntegerField(null=True, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('end_time', models.DateTimeField()),
                ('student_credits_applied', models.DecimalField(max_digits=19, decimal_places=4)),
                ('tutor_credits_applied', models.DecimalField(max_digits=19, decimal_places=4)),
                ('sesh_credits_applied', models.DecimalField(max_digits=19, decimal_places=4)),
                ('rating_1', models.IntegerField()),
                ('rating_2', models.IntegerField()),
                ('rating_3', models.IntegerField()),
                ('charge_id', models.CharField(max_length=100)),
                ('tutor_percentage', models.FloatField()),
                ('tutor_earnings', models.DecimalField(null=True, max_digits=19, decimal_places=4, blank=True)),
                ('student_cancelled', models.IntegerField()),
                ('tutor_cancelled', models.IntegerField()),
                ('was_cancelled', models.IntegerField()),
                ('cancellation_reason', models.CharField(max_length=30, null=True, blank=True)),
                ('cancellation_charge', models.IntegerField()),
                ('set_time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'past_seshes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ReportedProblem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('past_sesh_id', models.IntegerField(null=True, blank=True)),
                ('content', models.CharField(max_length=512, null=True, blank=True)),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'reported_problems',
                'managed': False,
            },
        ),
    ]
