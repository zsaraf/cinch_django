# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0001_initial'),
        ('student', '0002_studentclass'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentCourse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('course_group', models.ForeignKey(to='group.CourseGroup')),
                ('student', models.ForeignKey(to='student.Student')),
            ],
            options={
                'db_table': 'student_courses',
            },
        ),
        migrations.RemoveField(
            model_name='studentclass',
            name='student',
        ),
        migrations.DeleteModel(
            name='StudentClass',
        ),
    ]
