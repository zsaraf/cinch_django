# -*- coding: utf-8 -*-

from django.db import models
from apps.chatroom.models import ChatroomMember
from apps.notification.models import OpenNotification, NotificationType, PastNotification
from apps.university.models import Constant
from decimal import *
from rest_framework import exceptions
from django.db.models import Q
from sesh import settings

import stripe

stripe.api_key = settings.STRIPE_API_KEY


class OpenBid(models.Model):
    request_id = models.IntegerField()
    tutor = models.ForeignKey('tutor.Tutor')
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'open_bids'


class SeshRequest(models.Model):
    tutor = models.ForeignKey('tutor.Tutor', blank=True, null=True)
    student = models.ForeignKey('student.Student')
    school = models.ForeignKey('university.School')
    course = models.ForeignKey('university.Course', db_column='class_id')
    description = models.CharField(max_length=100, blank=True, null=True)
    processing = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    est_time = models.IntegerField(blank=True, null=True)
    num_people = models.IntegerField(default=1)
    hourly_rate = models.DecimalField(max_digits=19, decimal_places=4)
    expiration_time = models.DateTimeField(blank=True, null=True)
    is_instant = models.IntegerField(default=0)
    available_blocks = models.TextField(blank=True, null=True)
    location_notes = models.CharField(max_length=32, blank=True, null=True)
    discount = models.ForeignKey('university.Discount', blank=True, null=True)
    sesh_comp = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    status = models.IntegerField(default=0)
    has_seen = models.BooleanField(default=False)
    cancellation_reason = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'request'

    def get_estimated_wage(self):
        '''
        Get estimated wage for a request
        '''
        tutor_rate = self.adjusted_hourly_rate()
        return tutor_rate * Decimal(self.est_time / 60.0)

    def adjusted_hourly_rate(self):
        constants = Constant.objects.get(school_id=self.school.pk)
        additional_student_fee = (self.num_people - 1) * constants.additional_student_fee
        tutor_rate = (self.hourly_rate + self.sesh_comp + additional_student_fee) * Decimal(1.0 - constants.administrative_percentage)
        return tutor_rate

    def send_tutor_rejected_notification(self):
        '''
        Sends a notification to the student that the tutor rejected the request
        '''
        merge_vars = {
            "TUTOR_NAME": self.tutor.user.readable_name,
            "COURSE_NAME": self.course.get_readable_name()
        }
        data = {
            "request_id": self.pk
        }
        notification_type = NotificationType.objects.get(identifier="DIRECT_REQUEST_REJECTED")
        OpenNotification.objects.create(self.student.user, notification_type, data, merge_vars, None)

    def clear_notifications(self):
        '''
        After a request has ended, clear old notifications for all users
        '''
        from apps.tutor.models import TutorCourse
        import json

        tutor_classes = TutorCourse.objects.filter(course=self.course)
        refresh_type = NotificationType.objects.get(identifier="REFRESH_NOTIFICATIONS")
        new_request_notification_type = NotificationType.objects.get(identifier="NEW_REQUEST")
        new_direct_request_notification_type = NotificationType.objects.get(identifier="NEW_DIRECT_REQUEST")

        for tc in tutor_classes:
            notifications = OpenNotification.objects.filter(
                user=tc.tutor.user,
                notification_type__in=[new_request_notification_type, new_direct_request_notification_type]
            )
            for n in notifications:
                json_arr = json.loads(n.data)
                request_id = json_arr.get('request').get('id')
                if request_id == self.pk:
                    PastNotification.objects.create(data=n.data, user_id=n.user.pk, notification_type=n.notification_type, notification_vars=n.notification_vars, has_sent=n.has_sent, send_time=n.send_time)
                    OpenNotification.objects.get(pk=n.pk).delete()
            OpenNotification.objects.create(tc.tutor.user, refresh_type, None, None, None)

    def send_request_notification(self):
        '''
        Sends a notification to all eligible tutos that job is available
        '''
        from serializers import SeshRequestSerializer
        from apps.tutor.models import TutorCourse
        import locale

        locale.setlocale(locale.LC_ALL, '')

        merge_vars = {
            "CLOCK_SAYING": "🕒",
            "RATE_SAYING": "💵",
            "EST_TIME": self.est_time,
            "HOURLY_RATE": locale.currency(self.hourly_rate),
            "ESTIMATED_WAGE": locale.currency(self.get_estimated_wage()),
            "COURSE_NAME": self.course.get_readable_name()
        }
        data = {
            "request": SeshRequestSerializer(self).data
        }
        tutor_courses = TutorCourse.objects.filter(course=self.course)
        notification_type = NotificationType.objects.get(identifier="NEW_REQUEST")

        for tc in tutor_courses:
            OpenNotification.objects.create(tc.tutor.user, notification_type, data, merge_vars, None)

    def send_direct_request_notification(self):
        '''
        Sends a notification to the tutor that job is available
        '''
        from serializers import NotificationSeshRequestSerializer
        import locale

        locale.setlocale(locale.LC_ALL, '')

        merge_vars = {
            "STUDENT_NAME": self.student.user.readable_name,
            "COURSE_NAME": self.course.get_readable_name(),
            "HOURLY_RATE": locale.currency(self.adjusted_hourly_rate())
        }
        data = {
            "request": NotificationSeshRequestSerializer(self).data
        }
        notification_type = NotificationType.objects.get(identifier="NEW_DIRECT_REQUEST")
        OpenNotification.objects.create(self.tutor.user, notification_type, data, merge_vars, None)

    def send_tutor_accepted_notification(self, sesh):
        '''
        Sends a notification to the student that the request was accepted
        '''
        merge_vars = {
            "TUTOR_NAME": self.tutor.user.readable_name,
            "COURSE_NAME": self.course.get_readable_name()
        }
        data = {
            "sesh_id": sesh.pk
        }
        notification_type = NotificationType.objects.get(identifier="DIRECT_REQUEST_ACCEPTED")
        OpenNotification.objects.create(self.student.user, notification_type, data, merge_vars, None)


class OpenSesh(models.Model):
    past_request = models.OneToOneField('SeshRequest')
    tutor = models.ForeignKey('tutor.Tutor')
    timestamp = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(blank=True, null=True)
    has_started = models.IntegerField(default=0)
    student = models.ForeignKey('student.Student')
    set_time = models.DateTimeField(blank=True, null=True)
    is_instant = models.IntegerField(default=0)
    location_notes = models.CharField(max_length=32)
    has_received_start_time_approaching_reminder = models.IntegerField(blank=True, null=True)
    has_received_set_start_time_initial_reminder = models.IntegerField(blank=True, null=True)
    chatroom = models.ForeignKey('chatroom.Chatroom', blank=True, null=True)

    def send_has_started_notification(self):
        '''
        Sends a notification to student that the sesh has started
        '''
        merge_vars = {
            "TUTOR_NAME": self.tutor.user.readable_name
        }
        notification_type = NotificationType.objects.get(identifier="SESH_STARTED_STUDENT")
        OpenNotification.objects.create(self.student.user, notification_type, None, merge_vars, None)

    def send_set_time_notification(self, chatroom_activity, request):
        '''
        Sends a notification to the chatroom members
        '''
        from apps.chatroom.serializers import PNChatroomActivitySerializer

        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=self.tutor.user)
        merge_vars = {
            "TUTOR_NAME": self.tutor.user.readable_name,
            "SET_TIME": self.set_time
        }
        data = {
            "chatroom_activity": PNChatroomActivitySerializer(chatroom_activity, context={'request': request}).data,
            "set_time": self.set_time
        }
        notification_type = NotificationType.objects.get(identifier="SET_TIME_UPDATED")
        for cm in chatroom_members:
            if cm.notifications_enabled:
                OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    def send_set_location_notification(self, chatroom_activity, request):
        '''
        Sends a notification to the chatroom members
        '''
        from apps.chatroom.serializers import PNChatroomActivitySerializer

        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=self.user)
        merge_vars = {
            "STUDENT_NAME": self.student.user.readable_name,
            "LOCATION_NOTES": self.location_notes
        }
        data = {
            "chatroom_activity": PNChatroomActivitySerializer(chatroom_activity, context={'request': request}).data,
            "location_notes": self.location_notes
        }
        notification_type = NotificationType.objects.get(identifier="LOCATION_NOTES_UPDATED")
        for cm in chatroom_members:
            if cm.notifications_enabled:
                OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    class Meta:
        managed = False
        db_table = 'open_seshes'


class PastBid(models.Model):
    past_request = models.ForeignKey('SeshRequest')
    tutor = models.ForeignKey('tutor.Tutor')
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'past_bids'


class PastSesh(models.Model):
    past_request = models.OneToOneField('SeshRequest')
    tutor = models.ForeignKey('tutor.Tutor')
    student = models.ForeignKey('student.Student', blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField()
    student_credits_applied = models.DecimalField(default=0, max_digits=19, decimal_places=4)
    tutor_credits_applied = models.DecimalField(default=0, max_digits=19, decimal_places=4)
    sesh_credits_applied = models.DecimalField(default=0, max_digits=19, decimal_places=4)
    rating_1 = models.IntegerField(default=5)
    rating_2 = models.IntegerField(default=5)
    rating_3 = models.IntegerField(default=5)
    charge_id = models.CharField(max_length=100)
    tutor_percentage = models.FloatField(default=1.0)
    tutor_earnings = models.DecimalField(default=0, max_digits=19, decimal_places=4)
    student_cancelled = models.BooleanField(default=False)
    tutor_cancelled = models.BooleanField(default=False)
    was_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.CharField(default=None, max_length=30, blank=True, null=True)
    cancellation_charge = models.DecimalField(default=0, max_digits=19, decimal_places=4)
    set_time = models.DateTimeField(blank=True, null=True)
    chatroom = models.ForeignKey('chatroom.Chatroom', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'past_seshes'

    def charge_student(self, amount):
        from apps.transaction.models import OutstandingCharge

        # TODO send email with new outstanding charge

        user = self.student.user

        if user.stripe_customer_id is None:
            OutstandingCharge.objects.create(
                user=self.student.user,
                past_sesh=self,
                amount_owed=amount/100.0,
                code='no_payment_card'
            )

        # try:
        cards = stripe.Customer.retrieve(user.stripe_customer_id).sources.all(limit=5, object='card')
        if len(cards) == 0:
            OutstandingCharge.objects.create(
                user=self.student.user,
                past_sesh=self,
                amount_owed=amount/100.0,
                code='no_payment_card'
            )

        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            customer=user.stripe_customer_id,
            statement_descriptor='Sesh Tutoring',
            description='Thank you for choosing Sesh!'
        )

        brand = charge.source.brand
        last_four = charge.source.last4

        return (charge.id, brand, last_four)

        # except stripe.error.CardError, e:
        #     body = e.json_body
        #     err = body['error']
        #     code = err['code']

        #     OutstandingCharge.objects.create(
        #         user=self.student.user,
        #         past_sesh=self,
        #         amount_owed=amount/100.0,
        #         code=code
        #     )
        # except stripe.error.StripeError, e:
        #     # TODO handle exception
        #     return None
        # except Exception, e:
        #     # TODO handle exception
        #     return None

    def send_tutor_cancelled_notification(self):
        '''
        Sends a notification to student that tutor has cancelled
        '''
        search_str = "\"chatroom\": " + str(self.chatroom_id)
        existing_notifications = OpenNotification.objects.filter(user=self.student.user, data__icontains=search_str)
        for n in existing_notifications:
            PastNotification.objects.create(data=n.data, user_id=n.user.pk, notification_type=n.notification_type, notification_vars=n.notification_vars, has_sent=n.has_sent, send_time=n.send_time)
            OpenNotification.objects.get(pk=n.pk).delete()

        merge_vars = {
            "TUTOR_NAME": self.tutor.user.readable_name
        }
        notification_type = NotificationType.objects.get(identifier="SESH_CANCELLED_STUDENT")
        OpenNotification.objects.create(self.student.user, notification_type, None, merge_vars, None)

    def send_student_cancelled_notification(self):
        '''
        Sends a notification to tutor that student has cancelled
        '''
        search_str = "\"chatroom\": " + str(self.chatroom.pk)
        existing_notifications = OpenNotification.objects.filter(user=self.tutor.user, data__icontains=search_str)
        for n in existing_notifications:
            PastNotification.objects.create(data=n.data, user_id=n.user.pk, notification_type=n.notification_type, notification_vars=n.notification_vars, has_sent=n.has_sent, send_time=n.send_time)
            OpenNotification.objects.get(pk=n.pk).delete()

        merge_vars = {
            "STUDENT_NAME": self.student.user.readable_name
        }
        notification_type = NotificationType.objects.get(identifier="SESH_CANCELLED_TUTOR")
        OpenNotification.objects.create(self.tutor.user, notification_type, None, merge_vars, None)

    def send_has_ended_notifications(self):
        '''
        Clear existing notifications, sends a notifications to review sesh and refresh
        '''
        search_str = "\"chatroom\": " + str(self.chatroom_id)
        existing_notifications = OpenNotification.objects.filter(user__in=[self.student.user, self.tutor.user], data__icontains=search_str)
        for n in existing_notifications:
            PastNotification.objects.create(data=n.data, user_id=n.user.pk, notification_type=n.notification_type, notification_vars=n.notification_vars, has_sent=n.has_sent, send_time=n.send_time)
            OpenNotification.objects.get(pk=n.pk).delete()

        data = {
            "past_sesh_id": self.pk
        }
        notification_type = NotificationType.objects.get(identifier="SESH_REVIEW_STUDENT")
        OpenNotification.objects.create(self.student.user, notification_type, data, None, None)
        notification_type = NotificationType.objects.get(identifier="SESH_REVIEW_TUTOR")
        OpenNotification.objects.create(self.tutor.user, notification_type, data, None, None)

    def duration(self):
        if not self.was_cancelled:
            return (self.end_time - self.start_time).total_seconds()/3600
        else:
            return 0


class ReportedProblem(models.Model):
    past_sesh = models.ForeignKey(PastSesh, blank=True, null=True)
    content = models.CharField(max_length=512, blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'reported_problems'
