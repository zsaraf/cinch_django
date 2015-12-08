from apps.tutoring.models import OpenBid, OpenRequest, OpenSesh, PastBid, PastRequest, PastSesh, ReportedProblem
from rest_framework import viewsets
from apps.tutoring.serializers import *
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from apps.chatroom.models import Announcement, ChatroomActivity, ChatroomActivityType, ChatroomActivityTypeManager
from rest_framework.response import Response


class OpenBidViewSet(viewsets.ModelViewSet):
    queryset = OpenBid.objects.all()
    serializer_class = OpenBidSerializer


class OpenRequestViewSet(viewsets.ModelViewSet):
    queryset = OpenRequest.objects.all()
    serializer_class = OpenRequestSerializer


class OpenSeshViewSet(viewsets.ModelViewSet):
    queryset = OpenSesh.objects.all()
    serializer_class = OpenSeshSerializer

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def set_location_notes(self, request, pk=None):
        """
        Set location notes for an open sesh
        """
        user = request.user
        open_sesh = self.get_object()
        location_notes = request.POST.get('location_notes')
        open_sesh.location_notes = location_notes
        open_sesh.save()

        message = user.readable_name + " set the location to " + location_notes
        announcement = Announcement.objects.create(chatroom=open_sesh.chatroom, message=message)

        activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
        activity = ChatroomActivity.objects.create(chatroom=open_sesh.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)

        open_sesh.send_set_location_notification(activity)

        return Response()

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def set_start_time(self, request, pk=None):
        """
        Set start time for an open sesh
        """
        user = request.user
        open_sesh = self.get_object()
        set_time = request.POST.get('set_time')
        open_sesh.set_time = set_time
        open_sesh.save()

        message = user.readable_name + " set the start time for " + set_time
        announcement = Announcement.objects.create(chatroom=open_sesh.chatroom, message=message)

        activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
        activity = ChatroomActivity.objects.create(chatroom=open_sesh.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)

        open_sesh.send_set_time_notification(activity)

        return Response()


class PastBidViewSet(viewsets.ModelViewSet):
    queryset = PastBid.objects.all()
    serializer_class = PastBidSerializer


class PastRequestViewSet(viewsets.ModelViewSet):
    queryset = PastRequest.objects.all()
    serializer_class = PastRequestSerializer


class PastSeshViewSet(viewsets.ModelViewSet):
    queryset = PastSesh.objects.all()
    serializer_class = PastSeshSerializer


class ReportedProblemViewSet(viewsets.ModelViewSet):
    queryset = ReportedProblem.objects.all()
    serializer_class = ReportedProblemSerializer
