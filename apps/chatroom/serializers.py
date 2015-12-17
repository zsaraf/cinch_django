from rest_framework import serializers
from rest_framework import exceptions
from models import *
import logging
logger = logging.getLogger(__name__)


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement


class ChatroomActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatroomActivityType


class InteractionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interaction
        exclude = ['timestamp']


class ChatroomActivitySerializer(serializers.ModelSerializer):
    activity = serializers.SerializerMethodField()
    chatroom_activity_type = ChatroomActivityTypeSerializer()
    user_has_liked = serializers.SerializerMethodField()

    class Meta:
        model = ChatroomActivity

    def get_user_has_liked(self, obj):
        request = self.context.get('request', None)
        try:
            interaction = Interaction.objects.get(user=request.user, chatroom_activity=obj)
            return interaction.has_liked
        except Interaction.DoesNotExist:
            return False

    def get_activity(self, obj):
        if obj.chatroom_activity_type.is_message():
            return BasicMessageSerializer(Message.objects.get(pk=obj.activity_id), context={'request': self.context['request']}).data
        elif obj.chatroom_activity_type.is_announcement():
            return AnnouncementSerializer(Announcement.objects.get(pk=obj.activity_id), context={'request': self.context['request']}).data
        elif obj.chatroom_activity_type.is_upload():
            return UploadSerializer(Upload.objects.get(pk=obj.activity_id), context={'request': self.context['request']}).data
        elif obj.chatroom_activity_type.is_study_group():
            from apps.group.serializers import StudyGroupSerializer
            from apps.group.models import StudyGroup
            return StudyGroupSerializer(StudyGroup.objects.get(pk=obj.activity_id), context={'request': self.context['request']}).data
        else:
            return []


class ChatroomMemberSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = ChatroomMember

    def get_user(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.user).data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name']


class ChatroomSerializer(serializers.ModelSerializer):
    chatroom_activities = serializers.SerializerMethodField()
    chatroom_members = serializers.SerializerMethodField()
    # in the future tags would likely be chatroom-specific so including tags here
    tags = serializers.SerializerMethodField()
    unread_activity_count = serializers.SerializerMethodField()
    last_activity_id = serializers.SerializerMethodField()

    class Meta:
        model = Chatroom

    def get_last_activity_id(self, obj):
        l = list(ChatroomActivity.objects.filter(chatroom=obj)[:1])
        if l:
            return l[0].pk
        return None

    def get_chatroom_members(self, obj):
        return ChatroomMemberSerializer(ChatroomMember.objects.filter(chatroom=obj, is_past=False), many=True).data

    def get_unread_activity_count(self, obj):
        request = self.context.get('request', None)
        if request is not None:
            try:
                member = ChatroomMember.objects.get(user=request.user, chatroom=obj)
                return member.unread_activity_count
            except ChatroomMember.DoesNotExist:
                raise exceptions.NotFound("Chatroom member not found")
        raise exceptions.NotFound("Request not found")

    def get_tags(self, obj):
        return TagSerializer(Tag.objects.all(), many=True).data

    def get_chatroom_activities(self, obj):
        '''
        Limits the number of messages to [:5]
        '''
        return ChatroomActivitySerializer(ChatroomActivity.objects.filter(chatroom=obj).order_by('-id')[:50], many=True, context={'request': self.context['request']}).data


class UploadSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()
    tag = TagSerializer()

    class Meta:
        model = Upload

    def get_files(self, obj):
        return FileSerializer(File.objects.filter(upload=obj), many=True).data


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File


class BasicMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('message', 'chatroom_member', 'id')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
