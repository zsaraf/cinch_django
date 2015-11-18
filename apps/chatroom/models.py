from django.db import models


class OpenMessage(models.Model):
    sesh_id = models.IntegerField()
    to_user_id = models.IntegerField()
    from_user_id = models.IntegerField()
    content = models.CharField(max_length=1024)
    timestamp = models.DateTimeField()
    hasbeenread = models.IntegerField(db_column='hasBeenRead')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'open_messages'


class OpenChatroom(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    chatroom_type = models.ForeignKey('ChatroomType')
    last_updated = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'open_chatrooms'


class ChatroomType(models.Model):
    identifier = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'chatroom_types'


class PastChatroom(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    chatroom_type = models.ForeignKey('ChatroomType')
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'past_chatrooms'


class PastMessage(models.Model):
    past_sesh_id = models.IntegerField()
    to_user_id = models.IntegerField()
    from_user_id = models.IntegerField()
    content = models.CharField(max_length=1024)
    sent_time = models.DateTimeField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'past_messages'
