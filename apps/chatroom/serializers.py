from apps.chatroom.models import *
from rest_framework import serializers


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement


class ChatroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chatroom


class ChatroomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatroomType


class ChatroomActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatroomActivity


class ChatroomActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatroomActivityType


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message


class UnreadActivityCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnreadActivityCount
