# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('university', '0002_course'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('professor_name', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField()),
                ('course', models.ForeignKey(to='university.Course')),
            ],
            options={
                'db_table': 'course_groups',
            },
        ),
    ]
