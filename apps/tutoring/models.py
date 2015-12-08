from django.db import models
from apps.chatroom.models import ChatroomMember
from apps.notification.models import OpenNotification, NotificationType


class OpenBid(models.Model):
    request_id = models.IntegerField()
    tutor = models.ForeignKey('tutor.Tutor')
    timestamp = models.DateTimeField()
    tutor_latitude = models.FloatField(blank=True, null=True)
    tutor_longitude = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'open_bids'


class OpenRequest(models.Model):

    class Meta:
        managed = False
        db_table = 'open_requests'


class Request(models.Model):
    tutor = models.ForeignKey('tutor.Tutor')
    student = models.ForeignKey('student.Student')
    school = models.ForeignKey('university.School')
    course = models.ForeignKey('university.Course', db_column='class_id')
    description = models.CharField(max_length=100, blank=True, null=True)
    processing = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    est_time = models.IntegerField(blank=True, null=True)
    num_people = models.IntegerField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=19, decimal_places=4)
    expiration_time = models.DateTimeField(blank=True, null=True)
    is_instant = models.IntegerField(default=0)
    available_blocks = models.TextField(blank=True, null=True)
    location_notes = models.CharField(max_length=32, blank=True, null=True)
    discount = models.ForeignKey('university.Discount', blank=True, null=True)
    sesh_comp = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    status = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'request'

    def send_new_request_notification(self):
        '''
        Sends a notification to the tutor that job is available
        '''
        from serializers import RequestSerializer
        data = {
            "STUDENT_NAME": self.student.user.readable_name,
            "COURSE_NAME": self.course.get_readable_name()
        }
        merge_vars = {
            "request": RequestSerializer(self).data
        }
        notification_type = NotificationType.objects.get(identifier="NEW_DIRECT_REQUEST")
        OpenNotification.objects.create(self.tutor.user, notification_type, data, merge_vars, None)

    def send_tutor_accepted_notification(self, sesh):
        '''
        Sends a notification to the student that the request was accepted
        '''
        from serializers import OpenSeshSerializer
        data = {
            "TUTOR_NAME": self.tutor.user.readable_name,
            "COURSE_NAME": self.course.get_readable_name()
        }
        merge_vars = {
            "sesh": OpenSeshSerializer(sesh).data
        }
        notification_type = NotificationType.objects.get(identifier="DIRECT_REQUEST_ACCEPTED")
        OpenNotification.objects.create(self.tutor.user, notification_type, data, merge_vars, None)


class OpenSesh(models.Model):
    past_request = models.OneToOneField('Request')
    tutor = models.ForeignKey('tutor.Tutor')
    timestamp = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(blank=True, null=True)
    has_started = models.IntegerField(default=0)
    student = models.ForeignKey('student.Student')
    tutor_longitude = models.FloatField(blank=True, null=True)
    tutor_latitude = models.FloatField(blank=True, null=True)
    set_time = models.DateTimeField(blank=True, null=True)
    is_instant = models.IntegerField(default=0)
    location_notes = models.CharField(max_length=32)
    has_received_start_time_approaching_reminder = models.IntegerField(blank=True, null=True)
    has_received_set_start_time_initial_reminder = models.IntegerField(blank=True, null=True)
    chatroom = models.ForeignKey('chatroom.Chatroom', blank=True, null=True)

    def send_set_time_notification(self):
        '''
        Sends a notification to the chatroom members
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=self.tutor.user)
        data = {
            "TUTOR_NAME": self.tutor.user.readable_name,
            "SET_TIME": self.set_time
        }
        merge_vars = {
            "chatroom_id": self.chatroom.id,
            "set_time": self.set_time
        }
        notification_type = NotificationType.objects.get(identifier="SET_TIME_UPDATED")
        for cm in chatroom_members:
            OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    def send_set_location_notification(self):
        '''
        Sends a notification to the chatroom members
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=self.user)
        data = {
            "STUDENT_NAME": self.student.user.readable_name,
            "LOCATION_NOTES": self.location_notes
        }
        merge_vars = {
            "chatroom_id": self.chatroom.id,
            "location_notes": self.location_notes
        }
        notification_type = NotificationType.objects.get(identifier="LOCATION_NOTES_UPDATED")
        for cm in chatroom_members:
            OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    class Meta:
        managed = False
        db_table = 'open_seshes'


class PastBid(models.Model):
    past_request = models.ForeignKey('PastRequest')
    tutor = models.ForeignKey('tutor.Tutor')
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'past_bids'


class PastRequest(models.Model):
    student = models.ForeignKey('student.Student')
    course = models.ForeignKey('university.Course', db_column='class_id')  # Field renamed because it was a Python reserved word.
    school = models.ForeignKey('university.School')
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


class PastSesh(models.Model):
    past_request = models.OneToOneField('PastRequest')
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
    tutor_earnings = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
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
