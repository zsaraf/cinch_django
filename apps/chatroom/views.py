from rest_framework import viewsets
from apps.chatroom.serializers import *
from apps.chatroom.models import *


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer


class ChatroomViewSet(viewsets.ModelViewSet):
    queryset = Chatroom.objects.all()
    serializer_class = ChatroomSerializer


class ChatroomTypeViewSet(viewsets.ModelViewSet):
    queryset = ChatroomType.objects.all()
    serializer_class = ChatroomTypeSerializer


class ChatroomActivityViewSet(viewsets.ModelViewSet):
    queryset = ChatroomActivity.objects.all()
    serializer_class = ChatroomActivitySerializer


class ChatroomActivityTypeViewSet(viewsets.ModelViewSet):
    queryset = ChatroomActivityType.objects.all()
    serializer_class = ChatroomActivityTypeSerializer


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class UnreadActivityCountViewSet(viewsets.ModelViewSet):
    queryset = UnreadActivityCount.objects.all()
    serializer_class = UnreadActivityCountSerializer
