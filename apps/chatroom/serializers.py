from rest_framework import serializers
from models import *


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement


class ChatroomActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatroomActivityType


class ChatroomActivitySerializer(serializers.ModelSerializer):
    activity = serializers.SerializerMethodField()
    chatroom_activity_type = ChatroomActivityTypeSerializer()

    class Meta:
        model = ChatroomActivity

    def get_activity(self, obj):
        if obj.chatroom_activity_type.is_message():
            return BasicMessageSerializer(Message.objects.get(pk=obj.activity_id)).data
        elif obj.chatroom_activity_type.is_announcement():
            return AnnouncementSerializer(Announcement.objects.get(pk=obj.activity_id)).data
        elif obj.chatroom_activity_type.is_upload():
            return UploadSerializer(Upload.objects.get(pk=obj.activity_id)).data
        elif obj.chatroom_activity_type.is_study_group():
            from apps.group.serializers import StudyGroupSerializer
            from apps.group.models import StudyGroup
            return StudyGroupSerializer(StudyGroup.objects.get(pk=obj.activity_id)).data
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
    chatroom_members = ChatroomMemberSerializer(many=True, source="chatroommember_set")
    # in the future tags would likely be chatroom-specific so including tags here
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Chatroom

    def get_tags(self, obj):
        return TagSerializer(Tag.objects.all(), many=True).data

    def get_chatroom_activities(self, obj):
        '''
        Limits the number of messages to [:5]
        '''
        return ChatroomActivitySerializer(ChatroomActivity.objects.filter(chatroom=obj)[:20], many=True).data


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
