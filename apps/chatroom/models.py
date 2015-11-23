from django.db import models


class Announcement(models.Model):
    message = models.CharField(max_length=1024)
    chatroom = models.ForeignKey('chatroom.Chatroom')
    user = models.ForeignKey('account.User')

    class Meta:
        managed = False
        db_table = 'announcement'


class Chatroom(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'chatroom'


class ChatroomMember(models.Model):
    user = models.ForeignKey('account.User')
    chatroom = models.ForeignKey('chatroom.Chatroom')

    class Meta:
        managed = False
        db_table = 'chatroom_member'


class ChatroomActivity(models.Model):
    chatroom = models.ForeignKey('chatroom.Chatroom')
    chatroom_activity = models.ForeignKey('chatroom.ChatroomActivityType')
    activity_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'chatroom_activity'


class ChatroomActivityType(models.Model):
    identifier = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'chatroom_activity_type'


class File(models.Model):
    chatroom = models.ForeignKey('chatroom.Chatroom')
    src = models.CharField(max_length=256)
    name = models.CharField(max_length=128)
    user = models.ForeignKey('account.User')

    class Meta:
        managed = False
        db_table = 'file'


class Message(models.Model):
    message = models.CharField(max_length=1024)
    timestamp = models.DateTimeField()
    hasbeenread = models.IntegerField(db_column='hasBeenRead')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'message'


class UnreadActivityCount(models.Model):
    user = models.ForeignKey('account.User')
    chatroom = models.ForeignKey('chatroom.Chatroom')
    number = models.IntegerField()
    last_updated = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'unread_activity_count'
