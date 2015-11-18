from apps.chatroom.models import *
from rest_framework import serializers


class OpenMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenMessage


class OpenChatroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenChatroom


class ChatroomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatroomType


class PastChatroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = PastChatroom


class PastMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PastMessage
