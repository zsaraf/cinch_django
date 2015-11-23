from django.db import models
from sesh import settings

import logging
logger = logging.getLogger(__name__)


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

    def get_cards(self):
        """
        Gets both the stripe recipient and payment cards for the user instance
        """
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY

        def serialize_card_with_default(stripe_card, default_card_id):
            card_object = {}
            card_object['card_id'] = card.id
            card_object['last_four'] = card.last4
            card_object['type'] = card.brand
            card_object['is_recipient'] = False
            if (default_card_id == card.id):
                card_object['is_default'] = True
            else:
                card_object['is_default'] = False
            if (card.funding == "debit"):
                card_object['is_debit'] = True
            else:
                card_object['is_debit'] = False

            return card_object

        cards = []
        if (self.stripe_customer_id):
            cu = stripe.Customer.retrieve(self.stripe_customer_id)
            default_card_id = cu.default_source
            all_cards = cu.sources.data
            for card in all_cards:
                cards.append(serialize_card_with_default(card, default_card_id))

        if (self.stripe_recipient_id):
            rp = stripe.Recipient.retrieve(self.stripe_recipient_id)
            default_card_id = rp.default_card
            all_cards = rp.cards.data
            for card in all_cards:
                cards.append(serialize_card_with_default(card, default_card_id))

        return cards

    def is_authenticated(self):
        return True

    @property
    def readable_name(self):
        split_name = self.full_name.split(' ')
        first_name = split_name[0]
        last_name = split_name[len(split_name) - 1]

        return first_name + last_name[0]

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
