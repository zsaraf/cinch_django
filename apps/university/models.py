from django.db import models
from django.db.models import Q
import re
from .managers import SchoolManager
from rest_framework import exceptions
import json
import logging
logger = logging.getLogger(__name__)

class BonusPointAllocation(models.Model):
    school_id = models.IntegerField()
    sesh_completed_points = models.FloatField()
    tutor_referral_points = models.FloatField()
    monthly_point_goal = models.SmallIntegerField(blank=True, null=True)
    max_awards = models.SmallIntegerField()
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    bonus_amount = models.DecimalField(max_digits=19, decimal_places=4)
    user_referral_points = models.FloatField()
    direct_sesh_completed_points = models.FloatField()

    class Meta:
        managed = False
        db_table = 'bonus_point_allocation'


class Department(models.Model):
    school = models.ForeignKey('School', blank=True, null=True)
    name = models.CharField(max_length=20, blank=True, null=True)
    abbrev = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'departments'


class CourseManager(models.Manager):
    def search(self, user, search_term):
        search_term.strip()
        dept_name = ""
        class_num = ""
        all_courses = []
        letter_in_class = False

        matches = re.search(r'([^\d\s]+)', search_term)
        if (matches):
            potential_match = matches.group(0)
            num_depts = Department.objects.filter(school__id=user.school.pk, abbrev__istartswith=potential_match).order_by('abbrev')[:10].count()
            if num_depts == 0:
                letter_in_class = True
                dept_name = potential_match[:-1]
            else:
                dept_name = potential_match

        if ' ' in search_term:
            space_pos = search_term.find(' ')
            class_num = search_term[(space_pos + 1):]
        elif letter_in_class:
            class_num = search_term[len(dept_name):]
        else:
            num_matches = re.search(r'([0-9]+[a-zA-z]*)', search_term)
            if (num_matches):
                class_num = num_matches.group(0)

        logger.debug("Class: " + class_num)
        logger.debug("Dept Name: " + dept_name)
        depts = Department.objects.filter(school__id=user.school.pk, abbrev__istartswith=dept_name).order_by('abbrev')[:10]
        for dept in depts:
            dept_id = dept.pk
            courses = Course.objects.filter(department__id=dept_id, number__istartswith=class_num).order_by('number')[:10]
            all_courses.extend(courses)

        return all_courses


class Course(models.Model):

    school = models.ForeignKey('School')
    department = models.ForeignKey('Department', blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    number = models.CharField(max_length=5, blank=True, null=True)
    objects = CourseManager()

    class Meta:
        managed = False
        db_table = 'classes'

    def get_readable_name(self):
        return self.department.abbrev + str(self.number)


class Constant(models.Model):
    school_id = models.IntegerField()
    free_credits = models.DecimalField(max_digits=19, decimal_places=4)
    hourly_rate = models.DecimalField(max_digits=19, decimal_places=4)
    sesh_comp = models.DecimalField(max_digits=19, decimal_places=4)
    minimum_sesh_duration = models.IntegerField()
    max_bids = models.IntegerField()
    sesh_cancellation_timeout_minutes = models.IntegerField()
    administrative_percentage = models.FloatField()
    additional_student_fee = models.DecimalField(max_digits=19, decimal_places=4)
    late_cancellation_fee = models.IntegerField()
    user_share_amount = models.DecimalField(max_digits=19, decimal_places=4)
    friend_share_amount = models.DecimalField(max_digits=19, decimal_places=4)
    first_tutor_rate = models.DecimalField(max_digits=19, decimal_places=4)
    tutor_min = models.DecimalField(max_digits=19, decimal_places=4)
    instant_request_timeout = models.IntegerField()
    start_time_approaching_reminder = models.IntegerField()
    set_start_time_initial_reminder = models.IntegerField()
    set_start_time_reminder_interval = models.IntegerField()
    android_launch_date = models.DateTimeField()
    tutor_promo_recruiter_award = models.DecimalField(max_digits=19, decimal_places=4)
    tutor_promo_recruitee_award = models.DecimalField(max_digits=19, decimal_places=4)
    cancellation_administrative_percentage = models.DecimalField(max_digits=19, decimal_places=4)
    new_user_recruitment_award = models.DecimalField(max_digits=19, decimal_places=4)
    max_course_groups = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'constants'


class Discount(models.Model):
    credit_amount = models.FloatField()
    one_time_use = models.IntegerField()
    school = models.ForeignKey('School')
    exp_date = models.DateTimeField(blank=True, null=True)
    banner_message = models.CharField(max_length=200)
    num_uses = models.IntegerField(blank=True, null=True)
    learn_request_title = models.CharField(max_length=200, blank=True, null=True)
    banner_header = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'discounts'


class DiscountUse(models.Model):
    discount = models.ForeignKey('Discount', blank=True, null=True)
    user = models.ForeignKey('account.User', blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'discount_uses'


class School(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    enabled = models.BooleanField(default=False)
    email_domain = models.CharField(max_length=100)
    num_tutors = models.IntegerField()
    tutors_needed = models.IntegerField()
    ready_to_add_classes = models.BooleanField(default=False)
    requests_enabled = models.BooleanField(default=False)
    objects = SchoolManager()

    class Meta:
        managed = False
        db_table = 'schools'

    @property
    def line_position(self):
        if self.enabled:
            return -1

        return School.objects.filter(Q(num_tutors__gt=self.num_tutors) & Q(enabled=False)).count() + 1
