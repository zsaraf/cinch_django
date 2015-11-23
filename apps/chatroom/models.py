from django.db import models
from apps.notification.managers import *
from django.db.models import Q


class Announcement(models.Model):
    message = models.CharField(max_length=500)
    chatroom = models.ForeignKey('Chatroom')

    class Meta:
        managed = False
        db_table = 'announcement'


class Chatroom(models.Model):
    last_updated = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chatroom'


class ChatroomMember(models.Model):
    user = models.ForeignKey('account.User')
    chatroom = models.ForeignKey('chatroom.Chatroom')
    unread_activity_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'chatroom_member'


class ChatroomActivity(models.Model):
    chatroom = models.ForeignKey(Chatroom)
    chatroom_activity_type = models.ForeignKey('ChatroomActivityType')
    timestamp = models.DateTimeField()
    activity_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chatroom_activity'


class ChatroomActivityType(models.Model):
    identifier = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'chatroom_activity_type'


class File(models.Model):
    chatroom = models.ForeignKey(Chatroom)
    user = models.ForeignKey('account.User')
    src = models.CharField(max_length=250)
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'file'


class Message(models.Model):
    message = models.CharField(max_length=500)
    chatroom = models.ForeignKey(Chatroom)
    user = models.ForeignKey('account.User')

    def send_notifications(self):
        '''
        Sends a notification to the chatroom members
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=self)
        
        OpenNotificationManager.create(to_user_id, data, merge_vars, send_time)


    class Meta:
        managed = False
        db_table = 'message'
