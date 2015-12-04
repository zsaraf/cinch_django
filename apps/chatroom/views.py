from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
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

    # @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    # @detail_route(methods=['post'])
    # def upload_file(self, request, pk=None):
    # @list_route(methods=['get'])
    # def upload_file(self, request):

    #     import boto
    #     s3 = boto.connect_s3('AKIAIRQE6V6WEPIPVGVA', 'UcFmvCIzv41VhQ8uYv0GgSUpl1v4VY3o5HcenKeN')
    #     s3.connect_to_region('us-west-2')
    #     bucket = s3.lookup('sesh-tutoring-dev')
    #     if bucket:
    #         return Response("Success", 200)
    #     else:
    #         return Response("FAIL", 200)

    #     # upload_file = request.FILES['src']
    #     # name = request.POST.get('name')
    #     # user = request.user
    #     # chatroom = self.get_object()

    #     # form = FileUploadForm(request.POST, request.FILES)
    #     # if form.is_valid():
    #     #     File.objects.create(chatroom=chatroom, user=user, src=upload_file, name=name)
    #     # # File.objects.create(chatroom=chatroom, user=user, name=name)
    #     # return Response()


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

    def create(self, request):
        data_with_user = request.data
        data_with_user['user'] = request.user.id
        serializer = MessageSerializer(data=data_with_user)

        if serializer.is_valid():
            message = serializer.save()
            message.send_notifications()
            activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.MESSAGE)
            activity = ChatroomActivity.objects.create(chatroom=message.chatroom, chatroom_activity_type=activity_type, activity_id=message.pk)
        else:
            logger.debug("Invalid request.")

        return Response(serializer.errors, 200)
