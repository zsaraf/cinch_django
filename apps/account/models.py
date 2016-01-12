from django.db import models
from django.db.models import Q, Count, F
from sesh import settings
from datetime import datetime
from apps.university.serializers import DiscountSerializer
from .managers import TokenManager, DeviceManager
from random import randint
import stripe
import logging
from sesh.mandrill_utils import EmailManager

stripe.api_key = settings.STRIPE_API_KEY
logger = logging.getLogger(__name__)


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
    issue_time = models.DateTimeField(auto_now_add=True)
    objects = TokenManager()

    class Meta:
        managed = False
        db_table = 'tokens'


class User(models.Model):
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)
    share_code = models.CharField(max_length=10)
    token = models.ForeignKey(Token, on_delete=models.SET_NULL, blank=True, null=True)
    web_token_id = models.IntegerField()
    school = models.ForeignKey('university.School')
    is_verified = models.IntegerField()
    verification_id = models.CharField(max_length=100)
    stripe_customer_id = models.CharField(max_length=32, blank=True, null=True)
    stripe_recipient_id = models.CharField(max_length=32, blank=True, null=True)
    full_legal_name = models.CharField(max_length=100)
    profile_picture = models.CharField(max_length=250, blank=True, null=True)
    major = models.CharField(max_length=100)
    class_year = models.CharField(max_length=25, blank=True, null=True)
    bio = models.CharField(max_length=256)
    sesh_state = models.ForeignKey(SeshState)
    salt = models.CharField(max_length=25)
    notifications_enabled = models.BooleanField(default=False)
    completed_app_tour = models.BooleanField(default=False)
    is_rep = models.BooleanField(default=False)
    is_test = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_disabled = models.BooleanField(default=False)
    graduation_type = models.CharField(max_length=25, blank=True, null=True)
    chavatar_color = models.CharField(max_length=25, blank=True, null=True)

    def send_verification_email(self):

        # TODO implement server_name() call like in php
        link = "https://cinchtutoring.com/verify.html?verificationId=" + self.verification_id

        merge_vars = {
            'ACTIVATION_LINK': link,
            'FIRST_NAME': self.first_name
        }

        EmailManager.send_email(EmailManager.NEW_SESH_ACCOUNT, merge_vars, self.email, self.readable_name, None)

    def update_sesh_state(self, state_identifier, optional_data=None):
        from apps.notification.models import OpenNotification, NotificationType

        in_sesh = SeshState.objects.get(identifier=state_identifier)

        self.sesh_state = in_sesh
        self.save()

        if optional_data:
            data = optional_data
            data["state"] = state_identifier
        else:
            data = {
                "state": state_identifier
            }

        notification_type = NotificationType.objects.get(identifier="UPDATE_STATE")
        OpenNotification.objects.filter(user=self, notification_type=notification_type).delete()
        OpenNotification.objects.create(self, notification_type, data, None, None)

    def assign_chavatar(self):
        colors = ["PURPLE", "DEEPPURPLE", "BLACK", "BLUE", "RED", "GREEN", "ORANGE", "YELLOW"]
        index = randint(0, 7)
        self.chavatar_color = colors[index]
        self.save()

    @property
    def discounts(self):
        discounts = self.school.discount_set.annotate(
                                                        discount_num_uses=Count('discountuse')
                                                     ).filter(
                                                        Q(exp_date__isnull=True) | Q(exp_date__gt=datetime.now()),
                                                        Q(num_uses__isnull=True) | Q(num_uses__gt=F('discount_num_uses')),
                                                     ).exclude(
                                                        Q(one_time_use=1), Q(discountuse__user=self)
                                                     )
        return DiscountSerializer(discounts, many=True).data

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

        return first_name + " " + last_name[0] + "."

    @property
    def first_name(self):
        split_name = self.full_name.split(' ')
        return split_name[0]

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


class PromoType(models.Model):
    identifier = models.CharField(max_length=50)
    award_constant_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'promo_type'


class SharePromo(models.Model):
    new_user = models.ForeignKey(User, related_name="new_user")
    old_user = models.ForeignKey(User, related_name="old_user")
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    promo_type = models.ForeignKey(PromoType)
    is_past = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'share_promo'


class Device(models.Model):
    user = models.OneToOneField(User)
    token = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=100)
    device_model = models.CharField(max_length=40, blank=True, null=True)
    system_version = models.FloatField(blank=True, null=True)
    app_version = models.FloatField()
    timezone_name = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = DeviceManager()

    class Meta:
        managed = False
        db_table = 'devices'
