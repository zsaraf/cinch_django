from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from sesh import slack_utils
from itertools import chain
from .serializers import *
from .models import *
import tempfile
import json
import logging
logger = logging.getLogger(__name__)


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer


class ChatroomViewSet(viewsets.ModelViewSet):
    queryset = Chatroom.objects.all()
    serializer_class = ChatroomSerializer

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def get_first_activity_id(self, request, pk=None):
        chatroom = self.get_object()
        l = list(ChatroomActivity.objects.filter(chatroom=chatroom)[:1])
        if l:
            return Response({"first_activity_id": l[0].pk})
        return Response()

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        chatroom = self.get_object()
        last_activity_id = request.data['last_activity_id']
        user = request.user
        try:
            num_unread = ChatroomActivity.objects.filter(pk__gt=last_activity_id, chatroom=chatroom).count()
            chatroom_member = ChatroomMember.objects.get(user=user, chatroom=chatroom, is_past=False)
            chatroom_member.unread_activity_count = num_unread
            chatroom_member.save()
            OpenNotification.objects.send_badge_update(user)
            return Response()
        except ChatroomMember.DoesNotExist:
            return Response({"detail": "You are not a member of this chatroom"}, 405)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_notifications(self, request, pk=None):
        chatroom = self.get_object()
        user = request.user
        try:
            chatroom_member = ChatroomMember.objects.get(user=user, chatroom=chatroom, is_past=False)
            chatroom_member.notifications_enabled = not chatroom_member.notifications_enabled
            chatroom_member.save()
            return Response({"notifications_enabled": chatroom_member.notifications_enabled})
        except ChatroomMember.DoesNotExist:
            return Response({"detail": "You are not a member of this chatroom"}, 405)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def load_old_uploads_with_offset(self, request, pk=None):
        chatroom = self.get_object()
        max_id = request.data.get('max_id')
        tag_id = request.data.get('tag_id', None)

        tag = None
        if tag_id is not None:
            try:
                tag = Tag.objects.get(pk=tag_id)
            except Tag.DoesNotExist:
                return Response({"detail": "The requested tag does not exist"}, 405)

        try:
            ChatroomMember.objects.get(user=request.user, chatroom=chatroom, is_past=False)
        except ChatroomMember.DoesNotExist:
            return Response({"detail": "You are not a member of this chatroom"}, 405)

        upload_type = ChatroomActivityType.objects.get(identifier='upload')

        if tag is not None:
            activities = []
            count = 0
            for activity in ChatroomActivity.objects.filter(chatroom=chatroom, pk__lt=max_id, chatroom_activity_type=upload_type):
                upload = Upload.objects.get(pk=activity.activity_id)
                if upload.tag == tag:
                    count += 1
                    activities.append(activity)

                if count >= 50:
                    continue

            return Response(ChatroomActivitySerializer(activities, many=True, context={'request': request}).data)

        else:
            activity = ChatroomActivity.objects.filter(chatroom=chatroom, pk__lt=max_id, chatroom_activity_type=upload_type).order_by('-id')[:50]
            return Response(ChatroomActivitySerializer(activity, many=True, context={'request': request}).data)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def refresh_recent_uploads_with_offset(self, request, pk=None):
        chatroom = self.get_object()
        min_id = request.data.get('min_id')
        try:
            ChatroomMember.objects.get(user=request.user, chatroom=chatroom, is_past=False)
        except ChatroomMember.DoesNotExist:
            return Response({"detail": "You are not a member of this chatroom"}, 405)

        upload_type = ChatroomActivityType.objects.get(identifier='upload')
        activity = ChatroomActivity.objects.filter(chatroom=chatroom, pk__gte=min_id, chatroom_activity_type=upload_type).order_by('id')[:50]
        return Response(ChatroomActivitySerializer(activity, many=True, context={'request': request}).data)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def get_activity_with_offset(self, request, pk=None):
        chatroom = self.get_object()
        max_id = request.data.get('max_id')
        activity = ChatroomActivity.objects.filter(chatroom=chatroom, pk__lt=max_id).order_by('-id')[:5][::-1]
        if len(activity) > 0:
            if activity[0].parent_chatroom_activity is not None:
                parent_activity = ChatroomActivity.objects.filter(chatroom=chatroom, pk__lt=activity[0].pk, pk__gte=activity[0].parent_chatroom_activity.pk).order_by('id')
                activity = chain(parent_activity, activity)

        return Response(ChatroomActivitySerializer(activity, many=True, context={'request': request}).data)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def send_message(self, request, pk=None):

        user = request.user
        chatroom = self.get_object()
        text = request.data['message']
        embedded_data = None
        if 'embedded_data' in request.data:
            embedded_data = json.dumps(request.data['embedded_data'])

        if len(text) > 500:
            return Response({"detail": "Message must be less than 500 characters. Shorten it up!"}, 405)

        try:
            chatroom_member = ChatroomMember.objects.get(user=user, chatroom=chatroom, is_past=False)
            message = Message.objects.create(chatroom=chatroom, chatroom_member=chatroom_member, message=text)
            activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.MESSAGE)
            activity = ChatroomActivity.objects.create(chatroom=chatroom, chatroom_activity_type=activity_type, activity_id=message.pk)

            # post to slack TODO add detail
            slack_message = "[" + str(user.id) + "] " + user.email + " posted in " + chatroom.name + ":\n[" + str(message.id) + "] " + text
            slack_utils.send_simple_slack_message(slack_message)

            # process embedded data
            exclude_list = [chatroom_member.pk]
            if embedded_data is not None:
                json_arr = request.data['embedded_data']
                for obj in json_arr:
                    if obj['type'] == 'mention':
                        chatroom_member_id = obj['chatroom_member_id']
                        try:
                            mentioned_member = ChatroomMember.objects.get(pk=chatroom_member_id)
                            Mention.objects.create(message=message, chatroom_member=mentioned_member, start_index=obj['start_index'], end_index=obj['end_index'])
                            message.send_mention_notification(activity, request, chatroom_member_id)
                            exclude_list.append(chatroom_member_id)
                        except:
                            continue

            message.send_notifications_excluding_members(activity, request, exclude_list)
            return Response(ChatroomActivitySerializer(activity, context={'request': request}).data)

        except ChatroomMember.DoesNotExist:
            return Response({"detail": "You are not a member of this chatroom"}, 405)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def upload_from_web(self, request, pk=None):
        from wand.image import Image
        from wand.color import Color
        from wand import exceptions as wand_exceptions
        from apps.group.models import CourseGroup, CourseGroupMember

        chatroom = self.get_object()
        try:
            chatroom_member = ChatroomMember.objects.get(chatroom=chatroom, user=request.user)
        except ChatroomMember.DoesNotExist:
            # Create the course group member (is past)
            course_group = CourseGroup.objects.get(chatroom=chatroom)
            course_group_member = CourseGroupMember.objects.create(course_group=course_group, student=request.user.student, is_past=True)

            # Create the chatroom member (is past)
            chatroom_member = ChatroomMember.objects.create(user=request.user, chatroom=chatroom, is_past=True)

        name = request.data.get('name')
        is_anonymous = int(request.data.get('is_anonymous', False))
        tag = Tag.objects.get(pk=int(request.POST.get('tag_id')))

        new_upload = Upload.objects.create(chatroom_member=chatroom_member, chatroom=chatroom, name=name, tag=tag, is_anonymous=is_anonymous)
        all_urls = ""

        for fp in request.FILES:
            uploadedFile = request.data.get(fp)
            if uploadedFile.content_type == "application/pdf":
                image_pdf = Image(file=uploadedFile, resolution=250, background=Color("white"))
                image_jpeg = image_pdf.convert('jpeg')
                count = 0
                for single_img in image_jpeg.sequence:
                    img = Image(image=single_img, resolution=250)
                    temp = tempfile.TemporaryFile()
                    img.alpha_channel = False
                    img.save(file=temp)
                    url = new_upload.upload_file(temp)
                    temp.close()
                    all_urls = all_urls + url + "\n"
                    count += 1
                    if count >= 25:
                        break
                break
            url = new_upload.upload_file(uploadedFile)
            all_urls = all_urls + url + "\n"

        activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.UPLOAD)
        activity = ChatroomActivity.objects.create(chatroom=chatroom, chatroom_activity_type=activity_type, activity_id=new_upload.pk)
        new_upload.send_created_notification(activity, request, True)

        # post to slack TODO add detail
        message = request.user.email + " uploaded files to " + chatroom.name + ":\n[" + str(new_upload.id) + "] " + all_urls
        slack_utils.send_simple_slack_message(message)

        return Response(200)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def upload(self, request, pk=None):

        chatroom = self.get_object()

        try:
            chatroom_member = ChatroomMember.objects.get(chatroom=chatroom, user=request.user, is_past=False)
            name = request.data.get('name')
            is_anonymous = int(request.data.get('is_anonymous', 0))
            tag = Tag.objects.get(pk=int(request.POST.get('tag_id')))

            new_upload = Upload.objects.create(chatroom_member=chatroom_member, chatroom=chatroom, name=name, tag=tag, is_anonymous=is_anonymous)
            all_urls = ""
            for fp in request.FILES.getlist('file'):
                url = new_upload.upload_file(fp)
                all_urls = all_urls + url + "\n"

            activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.UPLOAD)
            activity = ChatroomActivity.objects.create(chatroom=chatroom, chatroom_activity_type=activity_type, activity_id=new_upload.pk)
            new_upload.send_created_notification(activity, request)

            # post to slack TODO add detail
            if (request.user.school_id != 923):
                message = request.user.email + " uploaded files to " + chatroom.name + ":\n[" + str(new_upload.id) + "] " + all_urls
                slack_utils.send_simple_slack_message(message)

            return Response(ChatroomActivitySerializer(activity, context={'request': request}).data)

        except ChatroomMember.DoesNotExist:
            return Response({"detail": "You are not a member of this chatroom"}, 405)

    @detail_route(methods=['get'], permission_classes=[IsAuthenticated])
    def get_chatroom_members(self, request, pk=None):
        chatroom = self.get_object()

        chatroom_members = ChatroomMember.objects.filter(chatroom=chatroom, is_past=False)
        return Response(ChatroomMemberSerializer(chatroom_members, many=True).data)


class InteractionViewSet(viewsets.ModelViewSet):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ChatroomMemberViewSet(viewsets.ModelViewSet):
    queryset = ChatroomMember.objects.all()
    serializer_class = ChatroomMemberSerializer


class ChatroomActivityViewSet(viewsets.ModelViewSet):
    queryset = ChatroomActivity.objects.all()
    serializer_class = ChatroomActivitySerializer

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def record_view(self, request, pk=None):
        user = request.user
        activity = self.get_object()
        try:
            interaction = Interaction.objects.get(chatroom_activity=activity, user=user)
            interaction.num_views = interaction.num_views + 1
            interaction.save()
        except Interaction.DoesNotExist:
            Interaction.objects.create(chatroom_activity=activity, user=user, num_views=1)

        activity.total_views = activity.total_views + 1
        activity.save()

        return Response(ChatroomActivitySerializer(activity, context={'request': request}).data)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_like(self, request, pk=None):
        user = request.user
        activity = self.get_object()

        try:
            interaction = Interaction.objects.get(chatroom_activity=activity, user=user)
            if interaction.has_liked:
                activity.total_likes = activity.total_likes - 1
            else:
                activity.total_likes = activity.total_likes + 1
            interaction.has_liked = not interaction.has_liked
            interaction.save()
        except Interaction.DoesNotExist:
            Interaction.objects.create(chatroom_activity=activity, user=user, has_liked=True)
            activity.total_likes = activity.total_likes + 1

        activity.save()

        return Response(ChatroomActivitySerializer(activity, context={'request': request}).data)


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
