from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import detail_route
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
    def get_activity_with_offset(self, request, pk=None):
        chatroom = self.get_object()
        max_id = request.data.get('max_id')
        activity = ChatroomActivity.objects.filter(chatroom=chatroom, pk__lt=max_id)[:50]
        return Response(ChatroomActivitySerializer(activity, many=True).data)

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

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def upload(self, request, pk=None):

        chatroom = self.get_object()
        chatroom_member = ChatroomMember.objects.get(chatroom=chatroom, user=request.user)
        name = request.POST.get('name')
        tag = Tag.objects.get(pk=int(request.POST.get('tag_id')))

        new_upload = Upload.objects.create(chatroom_member=chatroom_member, chatroom=chatroom, name=name, tag=tag)

        activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.UPLOAD)
        activity = ChatroomActivity.objects.create(chatroom=chatroom, chatroom_activity_type=activity_type, activity_id=new_upload.pk)
        new_upload.send_created_notification(activity)

        for fp in request.FILES.getlist('file'):
            new_upload.upload_file(fp)

        return Response(UploadSerializer(new_upload).data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ChatroomMemberViewSet(viewsets.ModelViewSet):
    queryset = ChatroomMember.objects.all()
    serializer_class = ChatroomMemberSerializer


class ChatroomActivityViewSet(viewsets.ModelViewSet):
    queryset = ChatroomActivity.objects.all()
    serializer_class = ChatroomActivitySerializer


class ChatroomActivityTypeViewSet(viewsets.ModelViewSet):
    queryset = ChatroomActivityType.objects.all()
    serializer_class = ChatroomActivityTypeSerializer


class UploadViewSet(viewsets.ModelViewSet):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
