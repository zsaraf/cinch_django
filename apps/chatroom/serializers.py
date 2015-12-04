from rest_framework import serializers
from .models import *


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement


class ChatroomSerializer(serializers.ModelSerializer):
    chatroom_activities = serializers.SerializerMethodField()
    chatroom_members = serializers.SerializerMethodField()

    class Meta:
        model = Chatroom

    def get_chatroom_activities(self, obj):
        '''
        Limits the number of messages to [:5]
        '''
        return ChatroomActivitySerializer(ChatroomActivity.objects.filter(chatroom=obj)[:20], many=True).data

    def get_chatroom_members(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer

        chatroom_members = []
        for chatroom_member in obj.chatroommember_set.all():
            chatroom_members.append(UserBasicInfoSerializer(chatroom_member.user).data)
        return chatroom_members


class ChatroomMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatroomMember


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
        elif obj.chatroom_activity_type.is_file():
            return FileSerializer(File.objects.get(pk=obj.activity_id)).data
        elif obj.chatroom_activity_type.is_study_group():
            from apps.group.serializers import StudyGroupSerializer
            from apps.group.models import StudyGroup
            return StudyGroupSerializer(StudyGroup.objects.get(pk=obj.activity_id)).data
        else:
            return []


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
