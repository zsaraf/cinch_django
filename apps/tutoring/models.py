# -*- coding: utf-8 -*-

from django.db import models
from apps.chatroom.models import ChatroomMember
from apps.notification.models import OpenNotification, NotificationType
from apps.university.models import Constant
from decimal import *


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
    num_people = models.IntegerField()
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
        from serializers import SeshRequestSerializer
        merge_vars = {}
        data = {
            "request": SeshRequestSerializer(self).data
        }
        notification_type = NotificationType.objects.get(identifier="DIRECT_REQUEST_REJECTED")
        OpenNotification.objects.create(self.student.user, notification_type, data, merge_vars, None)

    def send_cancelled_request_notification(self):
        '''
        Sends a notification to the tutor that the student cancelled their direct request
        '''
        from serializers import SeshRequestSerializer
        merge_vars = {}
        data = {
            "request": SeshRequestSerializer(self).data
        }
        notification_type = NotificationType.objects.get(identifier="DIRECT_REQUEST_CANCELLED")
        OpenNotification.objects.create(self.tutor.user, notification_type, data, merge_vars, None)

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
        from serializers import OpenSeshSerializer
        merge_vars = {
            "TUTOR_NAME": self.tutor.user.readable_name,
            "COURSE_NAME": self.course.get_readable_name()
        }
        data = {
            "sesh": OpenSeshSerializer(sesh).data
        }
        notification_type = NotificationType.objects.get(identifier="DIRECT_REQUEST_ACCEPTED")
        OpenNotification.objects.create(self.tutor.user, notification_type, data, merge_vars, None)


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

    def send_set_time_notification(self, chatroom_activity, request):
        '''
        Sends a notification to the chatroom members
        '''
        from apps.chatroom.serializers import ChatroomActivitySerializer

        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=self.tutor.user)
        merge_vars = {
            "TUTOR_NAME": self.tutor.user.readable_name,
            "SET_TIME": self.set_time
        }
        data = {
            "chatroom_id": ChatroomActivitySerializer(chatroom_activity, context={'request': request}).data,
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
        from apps.chatroom.serializers import ChatroomActivitySerializer

        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=self.user)
        merge_vars = {
            "STUDENT_NAME": self.student.user.readable_name,
            "LOCATION_NOTES": self.location_notes
        }
        data = {
            "chatroom_id": ChatroomActivitySerializer(chatroom_activity, context={'request': request}).data,
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
    student_credits_applied = models.DecimalField(max_digits=19, decimal_places=4)
    tutor_credits_applied = models.DecimalField(max_digits=19, decimal_places=4)
    sesh_credits_applied = models.DecimalField(max_digits=19, decimal_places=4)
    rating_1 = models.IntegerField()
    rating_2 = models.IntegerField()
    rating_3 = models.IntegerField()
    charge_id = models.CharField(max_length=100)
    tutor_percentage = models.FloatField()
    tutor_earnings = models.DecimalField(max_digits=19, decimal_places=4)
    student_cancelled = models.IntegerField()
    tutor_cancelled = models.IntegerField()
    was_cancelled = models.IntegerField()
    cancellation_reason = models.CharField(max_length=30, blank=True, null=True)
    cancellation_charge = models.IntegerField()
    set_time = models.DateTimeField(blank=True, null=True)
    chatroom = models.ForeignKey('chatroom.Chatroom', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'past_seshes'

    def duration(self):
        return (self.end_time - self.start_time).total_seconds()/3600


class ReportedProblem(models.Model):
    past_sesh = models.ForeignKey(PastSesh, blank=True, null=True)
    content = models.CharField(max_length=512, blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'reported_problems'
