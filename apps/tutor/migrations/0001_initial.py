# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OpenTutorPromo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_user_id', models.IntegerField()),
                ('tutor_email', models.CharField(max_length=100)),
                ('old_user_award', models.DecimalField(max_digits=19, decimal_places=4)),
                ('new_tutor_award', models.DecimalField(max_digits=19, decimal_places=4)),
                ('timestamp', models.DateTimeField()),
                ('tutor_added_classes', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'open_tutor_promos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PastTutorPromo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_user_id', models.IntegerField()),
                ('tutor_user_id', models.IntegerField()),
                ('old_user_award', models.DecimalField(max_digits=19, decimal_places=4)),
                ('new_tutor_award', models.DecimalField(max_digits=19, decimal_places=4)),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'past_tutor_promos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PendingTutor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('school_id', models.IntegerField()),
                ('ready_to_publish', models.IntegerField()),
                ('major', models.CharField(max_length=100)),
                ('class_year', models.CharField(max_length=25)),
                ('verification_id', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'pending_tutors',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PendingTutorClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('class_id', models.IntegerField()),
                ('pending_tutor_id', models.IntegerField()),
            ],
            options={
                'db_table': 'pending_tutor_classes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('enabled', models.IntegerField()),
                ('num_seshes', models.IntegerField()),
                ('ave_rating_1', models.FloatField()),
                ('ave_rating_2', models.FloatField()),
                ('ave_rating_3', models.FloatField()),
                ('credits', models.DecimalField(max_digits=19, decimal_places=4)),
                ('did_accept_terms', models.IntegerField()),
                ('bonus_points', models.FloatField()),
            ],
            options={
                'db_table': 'tutors',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TutorClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tutor_id', models.IntegerField()),
                ('class_id', models.IntegerField()),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'tutor_classes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TutorDepartment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tutor_id', models.IntegerField()),
                ('department_id', models.IntegerField()),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'tutor_departments',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TutorSignup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=100)),
                ('school_id', models.IntegerField()),
                ('timestamp', models.DateTimeField()),
                ('recruiter', models.CharField(max_length=250, null=True, blank=True)),
                ('reason', models.CharField(max_length=100, null=True, blank=True)),
            ],
            options={
                'db_table': 'tutor_signups',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TutorTier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(max_length=100, null=True, blank=True)),
                ('name', models.CharField(max_length=100)),
                ('sesh_prereq', models.IntegerField()),
                ('bonus_amount', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'tutor_tiers',
                'managed': False,
            },
        ),
    ]
