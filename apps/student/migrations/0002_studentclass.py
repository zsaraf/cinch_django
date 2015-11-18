# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('student', models.ForeignKey(to='student.Student')),
            ],
            options={
                'db_table': 'student_classes',
            },
        ),
    ]
