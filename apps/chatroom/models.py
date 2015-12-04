from django.db import models
from django import forms
from apps.notification.models import NotificationType, OpenNotification


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
    chatroom = models.ForeignKey(Chatroom)

    class Meta:
        managed = False
        db_table = 'chatroom_member'


class ChatroomActivity(models.Model):
    chatroom = models.ForeignKey(Chatroom)
    chatroom_activity_type = models.ForeignKey('ChatroomActivityType')
    timestamp = models.DateTimeField(auto_now_add=True)
    activity_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chatroom_activity'


class ChatroomActivityTypeManager(models.Manager):
    ANNOUNCEMENT = "announcement"
    FILE = "file"
    STUDY_GROUP = "study_group"
    MESSAGE = "message"
    def get_activity_type(self, type_identifier):
        return ChatroomActivityType.objects.get(identifier=type_identifier)
        

class ChatroomActivityType(models.Model):
    identifier = models.CharField(max_length=50)
    objects = ChatroomActivityTypeManager()

    class Meta:
        managed = False
        db_table = 'chatroom_activity_type'


def upload_file_to(instance, filename):
    import os
    from django.utils.timezone import now
    filename_base, filename_ext = os.path.splitext(filename)
    return 'images/files/%s%s' % (
        now().strftime("%Y%m%d%H%M%S"),
        filename_ext.lower(),
    )


class File(models.Model):
    chatroom = models.ForeignKey(Chatroom)
    chatroom_member = models.ForeignKey(ChatroomMember)
    src = models.FileField(upload_to='files', blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'file'


class FileUploadForm(forms.Form):
    src = forms.FileField()


class Message(models.Model):
    message = models.CharField(max_length=500)
    chatroom = models.ForeignKey(Chatroom)
    chatroom_member = models.ForeignKey(ChatroomMember)

    def send_notifications(self):
        '''
        Sends a notification to the chatroom members
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=self.chatroom_member.user)
        data = {
            "NAME": self.chatroom_member.user.readable_name,
            "MESSAGE": self.message
        }
        merge_vars = {
            "chatroom_id": self.chatroom.id,
            "message": self.message
        }
        notification_type = NotificationType.objects.get(identifier="NEW_MESSAGE")
        for cm in chatroom_members:
            OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    class Meta:
        managed = False
        db_table = 'message'
