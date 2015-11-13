# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class AddedOnlineCredit(models.Model):
    user_id = models.IntegerField()
    from_email = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'added_online_credit'


class AnonymousDevices(models.Model):
    token = models.CharField(max_length=200)
    type = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = 'anonymous_devices'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'


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


class CashOutAttempts(models.Model):
    user_id = models.IntegerField()
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    successful = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'cash_out_attempts'


class Classes(models.Model):
    school_id = models.IntegerField(blank=True, null=True)
    department_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    number = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'classes'


class Constants(models.Model):
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


class Departments(models.Model):
    school_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=20, blank=True, null=True)
    abbrev = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'departments'


class Devices(models.Model):
    user_id = models.IntegerField()
    token = models.CharField(max_length=200)
    type = models.CharField(max_length=100)
    device_model = models.CharField(max_length=40, blank=True, null=True)
    system_version = models.FloatField(blank=True, null=True)
    app_version = models.FloatField()
    timezone_name = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'devices'


class DiscountUses(models.Model):
    discount_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'discount_uses'


class Discounts(models.Model):
    credit_amount = models.FloatField()
    one_time_use = models.IntegerField()
    school_id = models.IntegerField()
    exp_date = models.DateTimeField(blank=True, null=True)
    banner_message = models.CharField(max_length=200)
    num_uses = models.IntegerField(blank=True, null=True)
    learn_request_title = models.CharField(max_length=200, blank=True, null=True)
    banner_header = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'discounts'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', blank=True, null=True)
    user = models.ForeignKey(AuthUser)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DoNotEmail(models.Model):
    email = models.CharField(max_length=100)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'do_not_email'


class EmailUserData(models.Model):
    user_id = models.IntegerField()
    received_timeout_credits = models.DateTimeField(blank=True, null=True)
    received_student_cancellation_credits = models.DateTimeField(blank=True, null=True)
    received_tutor_cancellation_credits = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'email_user_data'


class Favorites(models.Model):
    student_id = models.IntegerField(blank=True, null=True)
    tutor_id = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'favorites'


class NotificationTypes(models.Model):
    identifier = models.CharField(max_length=25)
    title = models.CharField(max_length=250, blank=True, null=True)
    message = models.CharField(max_length=250, blank=True, null=True)
    pn_message = models.CharField(max_length=250, blank=True, null=True)
    is_silent = models.IntegerField()
    priority = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'notification_types'


class OpenBids(models.Model):
    request_id = models.IntegerField()
    tutor_id = models.IntegerField()
    timestamp = models.DateTimeField()
    tutor_latitude = models.FloatField(blank=True, null=True)
    tutor_longitude = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'open_bids'


class OpenMessages(models.Model):
    sesh_id = models.IntegerField()
    to_user_id = models.IntegerField()
    from_user_id = models.IntegerField()
    content = models.CharField(max_length=1024)
    timestamp = models.DateTimeField()
    hasbeenread = models.IntegerField(db_column='hasBeenRead')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'open_messages'


class OpenNotifications(models.Model):
    user_id = models.IntegerField()
    data = models.TextField(blank=True, null=True)
    notification_type_id = models.IntegerField()
    notification_vars = models.TextField(blank=True, null=True)
    has_sent = models.IntegerField()
    send_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'open_notifications'


class OpenRequests(models.Model):
    student_id = models.IntegerField()
    school_id = models.IntegerField()
    class_id = models.IntegerField()
    description = models.CharField(max_length=100)
    processing = models.IntegerField()
    timestamp = models.DateTimeField()
    est_time = models.IntegerField()
    num_people = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    hourly_rate = models.DecimalField(max_digits=19, decimal_places=4)
    expiration_time = models.DateTimeField()
    is_instant = models.IntegerField()
    available_blocks = models.TextField()
    location_notes = models.CharField(max_length=32)
    discount_id = models.IntegerField(blank=True, null=True)
    sesh_comp = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'open_requests'


class OpenSeshes(models.Model):
    past_request_id = models.IntegerField()
    tutor_id = models.IntegerField()
    timestamp = models.DateTimeField()
    start_time = models.DateTimeField(blank=True, null=True)
    has_started = models.IntegerField()
    student_id = models.IntegerField()
    tutor_longitude = models.FloatField(blank=True, null=True)
    tutor_latitude = models.FloatField(blank=True, null=True)
    set_time = models.DateTimeField(blank=True, null=True)
    is_instant = models.IntegerField()
    location_notes = models.CharField(max_length=32)
    has_received_start_time_approaching_reminder = models.IntegerField(blank=True, null=True)
    has_received_set_start_time_initial_reminder = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'open_seshes'


class OpenSharePromos(models.Model):
    old_user_id = models.IntegerField()
    new_user_id = models.IntegerField()
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'open_share_promos'


class OpenTutorPromos(models.Model):
    old_user_id = models.IntegerField()
    tutor_email = models.CharField(max_length=100)
    old_user_award = models.DecimalField(max_digits=19, decimal_places=4)
    new_tutor_award = models.DecimalField(max_digits=19, decimal_places=4)
    timestamp = models.DateTimeField()
    tutor_added_classes = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'open_tutor_promos'


class OutstandingCharges(models.Model):
    past_sesh_id = models.IntegerField()
    user_id = models.IntegerField()
    amount_owed = models.DecimalField(max_digits=19, decimal_places=4)
    amount_payed = models.DecimalField(max_digits=19, decimal_places=4)
    resolved = models.IntegerField()
    code = models.CharField(max_length=100)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'outstanding_charges'


class PasswordChangeRequests(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    random_hash = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'password_change_requests'


class PastBids(models.Model):
    past_request_id = models.IntegerField()
    tutor_id = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'past_bids'


class PastBonuses(models.Model):
    user_id = models.IntegerField()
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    timestamp = models.DateTimeField()
    is_tier_bonus = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'past_bonuses'


class PastMessages(models.Model):
    past_sesh_id = models.IntegerField()
    to_user_id = models.IntegerField()
    from_user_id = models.IntegerField()
    content = models.CharField(max_length=1024)
    sent_time = models.DateTimeField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'past_messages'


class PastNotifications(models.Model):
    user_id = models.IntegerField()
    data = models.TextField(blank=True, null=True)
    notification_type_id = models.IntegerField()
    notification_vars = models.TextField(blank=True, null=True)
    has_sent = models.IntegerField()
    send_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'past_notifications'


class PastRequests(models.Model):
    student_id = models.IntegerField()
    class_id = models.IntegerField()
    school_id = models.IntegerField()
    description = models.CharField(max_length=100)
    time = models.DateTimeField()
    num_people = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    est_time = models.IntegerField()
    status = models.IntegerField()
    hourly_rate = models.DecimalField(max_digits=19, decimal_places=4)
    available_blocks = models.TextField()
    is_instant = models.IntegerField()
    expiration_time = models.DateTimeField()
    has_seen = models.IntegerField()
    discount_id = models.IntegerField(blank=True, null=True)
    cancellation_reason = models.CharField(max_length=30, blank=True, null=True)
    sesh_comp = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'past_requests'


class PastSeshes(models.Model):
    past_request_id = models.IntegerField()
    tutor_id = models.IntegerField()
    student_id = models.IntegerField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField()
    student_credits_applied = models.DecimalField(max_digits=19, decimal_places=4)
    tutor_credits_applied = models.DecimalField(max_digits=19, decimal_places=4)
    sesh_credits_applied = models.DecimalField(max_digits=19, decimal_places=4)
    rating_1 = models.IntegerField()
    rating_2 = models.IntegerField()
    rating_3 = models.IntegerField()
    charge_id = models.CharField(max_length=100)
    tutor_percentage = models.FloatField()
    tutor_earnings = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    student_cancelled = models.IntegerField()
    tutor_cancelled = models.IntegerField()
    was_cancelled = models.IntegerField()
    cancellation_reason = models.CharField(max_length=30, blank=True, null=True)
    cancellation_charge = models.IntegerField()
    set_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'past_seshes'


class PastSharePromos(models.Model):
    new_user_id = models.IntegerField()
    old_user_id = models.IntegerField()
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'past_share_promos'


class PastTutorPromos(models.Model):
    old_user_id = models.IntegerField()
    tutor_user_id = models.IntegerField()
    old_user_award = models.DecimalField(max_digits=19, decimal_places=4)
    new_tutor_award = models.DecimalField(max_digits=19, decimal_places=4)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'past_tutor_promos'


class PendingEmails(models.Model):
    user_id = models.IntegerField()
    category = models.IntegerField()
    tag = models.CharField(max_length=75)
    template_name = models.CharField(max_length=75)
    merge_vars = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pending_emails'


class PendingTutorClasses(models.Model):
    class_id = models.IntegerField()
    pending_tutor_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'pending_tutor_classes'


class PendingTutors(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    school_id = models.IntegerField()
    ready_to_publish = models.IntegerField()
    major = models.CharField(max_length=100)
    class_year = models.CharField(max_length=25)
    verification_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pending_tutors'


class PromoCodes(models.Model):
    code = models.CharField(max_length=25)
    value = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'promo_codes'


class RepRecruits(models.Model):
    recruiter = models.CharField(max_length=100)
    recruitee = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'rep_recruits'


class ReportedProblems(models.Model):
    past_sesh_id = models.IntegerField(blank=True, null=True)
    content = models.CharField(max_length=512, blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'reported_problems'


class Schools(models.Model):
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


class SeshStates(models.Model):
    identifier = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sesh_states'


class Student(models.Model):
    user_id = models.IntegerField()
    credits = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'students'


class Tokens(models.Model):
    session_id = models.CharField(max_length=100)
    issue_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tokens'


class TutorClasses(models.Model):
    tutor_id = models.IntegerField()
    class_id = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tutor_classes'


class TutorDepartments(models.Model):
    tutor_id = models.IntegerField()
    department_id = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tutor_departments'


class TutorSignups(models.Model):
    email = models.CharField(max_length=100)
    school_id = models.IntegerField()
    timestamp = models.DateTimeField()
    recruiter = models.CharField(max_length=250, blank=True, null=True)
    reason = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor_signups'


class TutorTiers(models.Model):
    identifier = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100)
    sesh_prereq = models.IntegerField()
    bonus_amount = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor_tiers'


class Tutor(models.Model):
    user_id = models.IntegerField()
    enabled = models.IntegerField()
    num_seshes = models.IntegerField()
    ave_rating_1 = models.FloatField()
    ave_rating_2 = models.FloatField()
    ave_rating_3 = models.FloatField()
    credits = models.DecimalField(max_digits=19, decimal_places=4)
    did_accept_terms = models.IntegerField()
    bonus_points = models.FloatField()

    class Meta:
        managed = False
        db_table = 'tutors'


class User(models.Model):
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)
    share_code = models.CharField(max_length=10)
    token_id = models.IntegerField()
    web_token_id = models.IntegerField()
    school_id = models.IntegerField()
    is_verified = models.IntegerField()
    verification_id = models.CharField(max_length=100)
    stripe_customer_id = models.CharField(max_length=32, blank=True, null=True)
    stripe_recipient_id = models.CharField(max_length=32, blank=True, null=True)
    full_legal_name = models.CharField(max_length=100)
    profile_picture = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    class_year = models.CharField(max_length=25, blank=True, null=True)
    bio = models.CharField(max_length=256)
    sesh_state_id = models.IntegerField()
    salt = models.CharField(max_length=25)
    notifications_enabled = models.IntegerField()
    completed_app_tour = models.IntegerField()
    is_rep = models.IntegerField()
    is_test = models.IntegerField()
    timestamp = models.DateTimeField()
    is_disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'users'
