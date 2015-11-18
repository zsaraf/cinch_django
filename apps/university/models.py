from django.db import models


class BonusPointAllocation(models.Model):
    school_id = models.IntegerField()
    sesh_completed_points = models.SmallIntegerField()
    tutor_referral_points = models.SmallIntegerField()
    monthly_point_goal = models.SmallIntegerField(blank=True, null=True)
    max_awards = models.SmallIntegerField()
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    bonus_amount = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'bonus_point_allocation'


class Course(models.Model):
    school = models.ForeignKey('School')
    department = models.ForeignKey('Department', blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    number = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'classes'


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

    class Meta:
        managed = False
        db_table = 'constants'


class Department(models.Model):
    school = models.ForeignKey('School', blank=True, null=True)
    name = models.CharField(max_length=20, blank=True, null=True)
    abbrev = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'departments'


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
    enabled = models.IntegerField()
    email_domain = models.CharField(max_length=100)
    num_tutors = models.IntegerField()
    tutors_needed = models.IntegerField()
    ready_to_add_classes = models.IntegerField()
    requests_enabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'schools'
