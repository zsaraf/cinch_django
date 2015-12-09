from apps.tutoring.models import OpenBid, SeshRequest, OpenSesh, PastBid, PastSesh, ReportedProblem
from rest_framework import viewsets
from apps.tutoring.serializers import *
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.http import require_POST
from apps.chatroom.models import Announcement, ChatroomActivity, ChatroomActivityType, ChatroomActivityTypeManager
from rest_framework.response import Response


class OpenBidViewSet(viewsets.ModelViewSet):
    queryset = OpenBid.objects.all()
    serializer_class = OpenBidSerializer


class SeshRequestViewSet(viewsets.ModelViewSet):
    queryset = SeshRequest.objects.all()
    serializer_class = SeshRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        '''
        Create a request
        '''
        from apps.student.models import Student
        from apps.university.models import Constant

        data = request.data
        data['student'] = Student.objects.get(user=request.user).pk
        data['hourly_rate'] = Constant.objects.get(school_id=request.user.school.pk).hourly_rate
        data['school'] = request.user.school.pk
        serializer = SeshRequestSerializer(data=data)
        if serializer.is_valid():
            sesh_request = serializer.save()
            if sesh_request.tutor:
                sesh_request.send_new_request_notification()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    @detail_route(methods=['post'])
    def cancel(self, request, pk=None):
        '''
        Cancel a request
        '''
        sesh_request = self.get_object()
        if not sesh_request.tutor or request.user.student != sesh_request.student:
            return Response("Student cannot cancel this request")
        if sesh_request.status > 0:
            return Response("It's too late to cancel this request")
        sesh_request.status = 2
        sesh_request.save()
        sesh_request.send_cancelled_request_notification()
        return Response("Request cancelled")

    @detail_route(methods=['post'])
    def accept(self, request, pk=None):
        '''
        Tutor accepts a direct request
        '''
        from apps.chatroom.models import Chatroom

        sesh_request = self.get_object()
        if not sesh_request.tutor or sesh_request.tutor != request.user.tutor:
            return Response("Tutor cannot respond to this request")
        sesh_request.status = 1
        sesh_request.save()
        name = sesh_request.course.get_readable_name() + " Sesh"
        desc = sesh_request.tutor.user.readable_name + " tutoring " + sesh_request.student.user.readable_name + " in " + sesh_request.course.get_readable_name()
        chatroom = Chatroom.objects.create(name=name, description=desc)
        sesh = OpenSesh.objects.create(past_request=sesh_request, tutor=sesh_request.tutor, student=sesh_request.student, chatroom=chatroom)
        sesh_request.send_tutor_accepted_notification(sesh)

        return Response(OpenSeshSerializer(sesh).data)


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
        location_notes = request.data.get('location_notes')
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


class PastSeshViewSet(viewsets.ModelViewSet):
    queryset = PastSesh.objects.all()
    serializer_class = PastSeshSerializer


class ReportedProblemViewSet(viewsets.ModelViewSet):
    queryset = ReportedProblem.objects.all()
    serializer_class = ReportedProblemSerializer
