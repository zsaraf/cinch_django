from rest_framework import serializers
from .models import *


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement


class ChatroomSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    chatroom_members = serializers.SerializerMethodField()

    class Meta:
        model = Chatroom

    def get_messages(self, obj):
        '''
        Limits the number of messages to [:5]
        '''
        return BasicMessageSerializer(Message.objects.filter(chatroom=obj)[:20], many=True).data

    def get_chatroom_members(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer

        chatroom_members = []
        for chatroom_member in obj.chatroommember_set.all():
            chatroom_members.append(UserBasicInfoSerializer(chatroom_member.user).data)
        return chatroom_members


class ChatroomMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatroomMember


class ChatroomActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatroomActivity


class ChatroomActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatroomActivityType


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File


class BasicMessageSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('message', 'user')

    def get_user(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.user).data


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
