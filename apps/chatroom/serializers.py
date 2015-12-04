from rest_framework import serializers
from .models import *


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement


class ChatroomSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Chatroom

    def get_messages(self, obj):
        '''
        Limits the number of messages to [:5]
        '''
        return BasicMessageSerializer(Message.objects.filter(chatroom=obj)[:20], many=True).data


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

    class Meta:
        model = Message
        fields = ('message', 'chatroom_member')



class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
