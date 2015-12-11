from django.db import models
from django.utils.crypto import get_random_string
from sesh.s3utils import upload_png_to_s3
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
    chatroom = models.ForeignKey('Chatroom')
    unread_activity_count = models.IntegerField(default=0)

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

    def save(self, *args, **kwargs):
        if not self.pk:
            # only happens when not in db
            chatroom_members = []
            if self.chatroom_activity_type.is_message():
                message = Message.objects.get(pk=self.activity_id)
                chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=message.chatroom_member.user)
            elif self.chatroom_activity_type.is_announcement():
                chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom)
            elif self.chatroom_activity_type.is_upload():
                new_upload = Upload.objects.get(pk=self.activity_id)
                chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=new_upload.chatroom_member.user)
            elif self.chatroom_activity_type.is_study_group():
                from apps.group.models import StudyGroup
                group = StudyGroup.objects.get(pk=self.activity_id)
                chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=group.user)
            for member in chatroom_members:
                member.unread_activity_count = member.unread_activity_count + 1
                member.save()

        super(ChatroomActivity, self).save(*args, **kwargs)


class ChatroomActivityTypeManager(models.Manager):
    ANNOUNCEMENT = "announcement"
    UPLOAD = "upload"
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

    def is_announcement(self):
        return self.identifier == "announcement"

    def is_upload(self):
        return self.identifier == "upload"

    def is_study_group(self):
        return self.identifier == "study_group"

    def is_message(self):
        return self.identifier == "message"


class Upload(models.Model):
    chatroom = models.ForeignKey(Chatroom)
    chatroom_member = models.ForeignKey(ChatroomMember)
    name = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    tag = models.ForeignKey('Tag')

    def upload_file(self, fp):
        file_name = '%s.png' % get_random_string(20)
        url = upload_png_to_s3(fp, 'images/files', file_name)
        File.objects.create(src=url, upload=self)

    def send_created_notification(self, chatroom_activity):
        import serializers
        '''
        Sends a notification to the chatroom members
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=self.chatroom_member.user)
        merge_vars = {
            "CREATOR_NAME": self.chatroom_member.user.readable_name,
            "CHATROOM_NAME": self.chatroom.name
        }
        data = {
            "chatroom_activity": serializers.ChatroomActivitySerializer(chatroom_activity).data,
        }
        notification_type = NotificationType.objects.get(identifier="NEW_UPLOAD")
        for cm in chatroom_members:
            OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    class Meta:
        managed = False
        db_table = 'upload'


class Interaction(models.Model):
    chatroom_activity = models.ForeignKey(ChatroomActivity)
    user = models.ForeignKey('account.User')
    num_views = models.IntegerField(default=0)
    has_liked = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'interaction'


class File(models.Model):
    upload = models.ForeignKey(Upload)
    src = models.CharField(max_length=250, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'file'


class Tag(models.Model):
    name = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tag'


class Message(models.Model):
    message = models.CharField(max_length=500)
    chatroom = models.ForeignKey(Chatroom)
    chatroom_member = models.ForeignKey(ChatroomMember)

    def send_notifications(self, chatroom_activity):
        import serializers
        '''
        Sends a notification to the chatroom members
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=self.chatroom_member.user)
        merge_vars = {
            "NAME": self.chatroom_member.user.readable_name,
            "MESSAGE": self.message
        }
        data = {
            "chatroom_activity": serializers.ChatroomActivitySerializer(chatroom_activity).data,
        }
        notification_type = NotificationType.objects.get(identifier="NEW_MESSAGE")
        for cm in chatroom_members:
            OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    class Meta:
        managed = False
        db_table = 'message'
