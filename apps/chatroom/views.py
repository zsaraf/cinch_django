from rest_framework import viewsets
from apps.chatroom.serializers import *
from apps.chatroom.models import *


class OpenMessageViewSet(viewsets.ModelViewSet):
    queryset = OpenMessage.objects.all()
    serializer_class = OpenMessageSerializer


class OpenChatroomViewSet(viewsets.ModelViewSet):
    queryset = OpenChatroom.objects.all()
    serializer_class = OpenChatroomSerializer


class ChatroomTypeViewSet(viewsets.ModelViewSet):
    queryset = ChatroomType.objects.all()
    serializer_class = ChatroomTypeSerializer


class PastChatroomViewSet(viewsets.ModelViewSet):
    queryset = PastChatroom.objects.all()
    serializer_class = PastChatroomSerializer


class PastMessageViewSet(viewsets.ModelViewSet):
    queryset = PastMessage.objects.all()
    serializer_class = PastMessageSerializer
