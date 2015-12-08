from rest_framework import viewsets
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from django.utils.crypto import get_random_string
import os
from .serializers import *
from .models import *
import logging
logger = logging.getLogger(__name__)


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer


class ChatroomViewSet(viewsets.ModelViewSet):
    queryset = Chatroom.objects.all()
    serializer_class = ChatroomSerializer

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def send_message(self, request, pk=None):
        data_with_user = request.data
        chatroom = self.get_object()
        chatroom_member = ChatroomMember.objects.get(chatroom=chatroom, user=request.user)
        data_with_user['user'] = request.user.id
        data_with_user['chatroom'] = chatroom.pk
        data_with_user['chatroom_member'] = chatroom_member.pk
        serializer = MessageSerializer(data=data_with_user)
        if serializer.is_valid():
            message = serializer.save()
            activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.MESSAGE)
            activity = ChatroomActivity.objects.create(chatroom=message.chatroom, chatroom_activity_type=activity_type, activity_id=message.pk)
            message.send_notifications(activity)
            return Response(ChatroomActivitySerializer(activity).data)
        else:
            logger.debug("Invalid request.")

        return Response(serializer.errors)

    # def upload_file(self, request):
    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def upload_file(self, request, pk=None):

        import boto
        from boto.s3.key import Key

        chatroom = self.get_object()
        chatroom_member = ChatroomMember.objects.get(chatroom=chatroom, user=request.user)
        file_name = request.POST.get('file_name')

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        # connect to the bucket
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(bucket_name)

        key = '%s.png' % get_random_string(20)
        path = 'images/files'
        full_key_name = os.path.join(path, key)
        fp = request.FILES['src']

        # create a key to keep track of our file in the storage
        k = Key(bucket)
        k.key = full_key_name
        k.set_contents_from_file(fp)

        # we need to make it public so it can be accessed publicly
        # using a URL like http://sesh-tutoring-dev.s3.amazonaws.com/file_name.png
        k.make_public()

        url = settings.S3_URL + "/" + full_key_name
        File.objects.create(chatroom_member=chatroom_member, src=url, chatroom=chatroom, name=file_name)
        return Response()


class ChatroomMemberViewSet(viewsets.ModelViewSet):
    queryset = ChatroomMember.objects.all()
    serializer_class = ChatroomMemberSerializer


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
    permission_classes = [IsAuthenticated]
