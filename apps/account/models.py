from django.db import models


class Device(models.Model):
    user = models.OneToOneField('User')
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


class DoNotEmail(models.Model):
    email = models.CharField(max_length=100)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'do_not_email'


class EmailUserData(models.Model):
    user = models.OneToOneField('User')
    received_timeout_credits = models.DateTimeField(blank=True, null=True)
    received_student_cancellation_credits = models.DateTimeField(blank=True, null=True)
    received_tutor_cancellation_credits = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'email_user_data'


class PasswordChangeRequest(models.Model):
    user = models.OneToOneField('User', blank=True, null=True)
    random_hash = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'password_change_requests'


class PastBonus(models.Model):
    user_id = models.IntegerField()
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    timestamp = models.DateTimeField()
    is_tier_bonus = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'past_bonuses'


class PromoCode(models.Model):
    code = models.CharField(max_length=25)
    value = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'promo_codes'


class SeshState(models.Model):
    identifier = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sesh_states'


class Token(models.Model):
    session_id = models.CharField(max_length=100)
    issue_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tokens'


class User(models.Model):
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)
    share_code = models.CharField(max_length=10)
    token = models.ForeignKey(Token, blank=True, null=True)
    web_token_id = models.IntegerField()
    school = models.ForeignKey('university.School')
    is_verified = models.IntegerField()
    verification_id = models.CharField(max_length=100)
    stripe_customer_id = models.CharField(max_length=32, blank=True, null=True)
    stripe_recipient_id = models.CharField(max_length=32, blank=True, null=True)
    full_legal_name = models.CharField(max_length=100)
    profile_picture = models.CharField(max_length=250)
    major = models.CharField(max_length=100)
    class_year = models.CharField(max_length=25, blank=True, null=True)
    bio = models.CharField(max_length=256)
    sesh_state = models.ForeignKey(SeshState)
    salt = models.CharField(max_length=25)
    notifications_enabled = models.IntegerField()
    completed_app_tour = models.IntegerField()
    is_rep = models.IntegerField()
    is_test = models.IntegerField()
    timestamp = models.DateTimeField()
    is_disabled = models.IntegerField()

    def is_authenticated(self):
        return True

    @property
    def is_admin(self):
        return self.is_test

    @property
    def is_superuser(self):
        return self.is_test

    @property
    def is_staff(self):
        return self.is_test

    class Meta:
        managed = False
        db_table = 'users'
