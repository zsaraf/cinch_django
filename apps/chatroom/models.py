from django.db import models
from django.utils.crypto import get_random_string
from sesh.s3utils import upload_image_to_s3, get_true_image_size
from apps.notification.models import NotificationType, OpenNotification
from rest_framework.response import Response
import json
import logging
logger = logging.getLogger(__name__)


class Announcement(models.Model):
    user = models.ForeignKey('account.User')
    chatroom = models.ForeignKey('Chatroom')
    announcement_type = models.ForeignKey('AnnouncementType')

    class Meta:
        managed = False
        db_table = 'announcement'

    def send_notifications(self, request, chatroom_activity):
        '''
        Sends a notification to the chatroom members
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=chatroom_activity.chatroom, is_past=False).exclude(user=self.user)
        data = chatroom_activity.get_pn_data(request)
        notification_type = NotificationType.objects.get(identifier="NEW_ANNOUNCEMENT")

        for cm in chatroom_members:
            OpenNotification.objects.create(cm.user, notification_type, data, None, None, cm.notifications_enabled)


class AnnouncementType(models.Model):
    identifier = models.CharField(max_length=250)
    third_person_text = models.CharField(max_length=250)
    second_person_text = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'announcement_type'


class Chatroom(models.Model):
    last_updated = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'chatroom'

    def get_chatroom_activities(self):
        return ChatroomActivity.objects.filter(chatroom=self).order_by('-id')[:50]


class ChatroomMember(models.Model):
    user = models.ForeignKey('account.User')
    chatroom = models.ForeignKey('Chatroom')
    notifications_enabled = models.BooleanField(default=True)
    unread_activity_count = models.IntegerField(default=0)
    is_past = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'chatroom_member'


class ChatroomActivity(models.Model):
    chatroom = models.ForeignKey(Chatroom)
    chatroom_activity_type = models.ForeignKey('ChatroomActivityType')
    timestamp = models.DateTimeField(auto_now_add=True)
    activity_id = models.IntegerField(blank=True, null=True)
    total_views = models.IntegerField(default=0)
    total_likes = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'chatroom_activity'

    def get_pn_data(self, request):
        from serializers import PNChatroomActivitySerializer
        data = {}
        full_object = PNChatroomActivitySerializer(self, context={'request': request}).data
        logger.debug(len(json.dumps(full_object)))
        if len(json.dumps(full_object)) > 1500:
            data['chatroom_activity_id'] = self.pk
        else:
            data['chatroom_activity'] = full_object

        data['chatroom_id'] = self.chatroom.id
        return data

    def save(self, *args, **kwargs):
        if not self.pk:
            # only happens when not in db
            chatroom_members = []
            if self.chatroom_activity_type.is_message():
                message = Message.objects.get(pk=self.activity_id)
                chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom, is_past=False).exclude(user=message.chatroom_member.user)
            elif self.chatroom_activity_type.is_announcement():
                announcement = Announcement.objects.get(pk=self.activity_id)
                chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom, is_past=False).exclude(user=announcement.user)
            elif self.chatroom_activity_type.is_upload():
                new_upload = Upload.objects.get(pk=self.activity_id)
                chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom, is_past=False).exclude(user=new_upload.chatroom_member.user)
            elif self.chatroom_activity_type.is_study_group():
                from apps.group.models import StudyGroup
                group = StudyGroup.objects.get(pk=self.activity_id)
                chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom, is_past=False).exclude(user=group.user)
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
    is_anonymous = models.BooleanField(default=False)

    def upload_file(self, fp):

        fp.seek(0)
        (width, height) = get_true_image_size(fp)
        fp.seek(0)

        file_name = '%s.jpeg' % get_random_string(20)
        url = upload_image_to_s3(fp, 'images/files', file_name)

        File.objects.create(src=url, upload=self, width=width, height=height)

        return url

    def send_created_notification(self, chatroom_activity, request):
        import serializers
        from apps.group.models import CourseGroup, StudyGroup, Conversation
        from apps.tutoring.models import OpenSesh
        '''
        Sends a notification to the chatroom members
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom, is_past=False).exclude(user=self.chatroom_member.user)
        creator_name = self.chatroom_member.user.readable_name
        if self.is_anonymous:
            creator_name = "Someone"
        merge_vars = {
            "CREATOR_NAME": creator_name,
            "CHATROOM_NAME": self.chatroom.name
        }
        data = chatroom_activity.get_pn_data(request)

        notification_type = None
        if CourseGroup.objects.filter(chatroom=self.chatroom, is_past=False).count() > 0:
            notification_type = NotificationType.objects.get(identifier="NEW_UPLOAD_COURSE_GROUP")
        elif StudyGroup.objects.filter(chatroom=self.chatroom, is_past=False).count() > 0:
            notification_type = NotificationType.objects.get(identifier="NEW_UPLOAD_STUDY_GROUP")
        elif OpenSesh.objects.filter(chatroom=self.chatroom).count() > 0:
            notification_type = NotificationType.objects.get(identifier="NEW_UPLOAD_SESH")
        elif Conversation.objects.filter(chatroom=self.chatroom).count() > 0:
            notification_type = NotificationType.objects.get(identifier="NEW_UPLOAD_CONVERSATION")
        else:
            return Response({"detail": "Sorry, something's wrong with the network. Be back soon!"}, 405)
        for cm in chatroom_members:
            OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None, cm.notifications_enabled)

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
    width = models.IntegerField()
    height = models.IntegerField()

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

    def send_mention_notification(self, chatroom_activity, request, chatroom_member_id):
        '''
        Sends a notification to someone who was mentioned in a message
        '''
        from apps.group.models import CourseGroup, StudyGroup
        chatroom_member = ChatroomMember.objects.get(pk=chatroom_member_id)

        merge_vars = {
            "NAME": self.chatroom_member.user.readable_name,
            "CHATROOM_NAME": self.chatroom.name
        }
        data = chatroom_activity.get_pn_data(request)
        notification_type = NotificationType.objects.get(identifier="NEW_MENTION")
        if CourseGroup.objects.filter(chatroom=self.chatroom, is_past=False).count() > 0:
            notification_type = NotificationType.objects.get(identifier="NEW_MENTION_COURSE_GROUP")
        elif StudyGroup.objects.filter(chatroom=self.chatroom, is_past=False).count() > 0:
            notification_type = NotificationType.objects.get(identifier="NEW_MENTION_STUDY_GROUP")

        OpenNotification.objects.create(chatroom_member.user, notification_type, data, merge_vars, None, chatroom_member.notifications_enabled)

    def send_notifications_excluding_members(self, chatroom_activity, request, exclude_list):
        from apps.group.models import CourseGroup, StudyGroup
        '''
        Sends a notification to the chatroom members
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom, is_past=False).exclude(id__in=exclude_list)

        display_message = self.message
        if (len(self.message) > 150):
            display_message = self.message[:150] + "..."

        merge_vars = {
            "NAME": self.chatroom_member.user.readable_name,
            "MESSAGE": display_message,
            "CHATROOM_NAME": self.chatroom.name
        }
        data = chatroom_activity.get_pn_data(request)
        notification_type = NotificationType.objects.get(identifier="NEW_MESSAGE")
        if CourseGroup.objects.filter(chatroom=self.chatroom, is_past=False).count() > 0:
            notification_type = NotificationType.objects.get(identifier="NEW_MESSAGE_COURSE_GROUP")
        elif StudyGroup.objects.filter(chatroom=self.chatroom, is_past=False).count() > 0:
            notification_type = NotificationType.objects.get(identifier="NEW_MESSAGE_STUDY_GROUP")

        for cm in chatroom_members:
            OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None, cm.notifications_enabled)

    class Meta:
        managed = False
        db_table = 'message'


# class Mention(models.Model):
#     start_index = models.IntegerField()
#     end_index = models.IntegerField()
#     chatroom_member = models.ForeignKey(ChatroomMember)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     message = models.ForeignKey(Message)

#     class Meta:
#         managed = False
#         db_table = 'mention'
