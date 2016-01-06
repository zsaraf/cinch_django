from apps.tutoring.models import OpenBid, SeshRequest, OpenSesh, PastBid, PastSesh, ReportedProblem
from rest_framework import viewsets
from rest_framework import exceptions
from apps.tutoring.serializers import *
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from apps.chatroom.models import Announcement, AnnouncementType, ChatroomActivity, ChatroomActivityType, ChatroomActivityTypeManager
from apps.chatroom.serializers import ChatroomActivitySerializer
from rest_framework.response import Response
from decimal import *
from django.utils import dateparse


class OpenBidViewSet(viewsets.ModelViewSet):
    queryset = OpenBid.objects.all()
    serializer_class = OpenBidSerializer


class SeshRequestViewSet(viewsets.ModelViewSet):
    queryset = SeshRequest.objects.all()
    serializer_class = SeshRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        '''
        create a request
        '''
        from apps.student.models import Student
        from apps.tutor.models import Tutor
        from apps.university.models import Course, Discount, Constant

        student = Student.objects.get(user=request.user)

        try:
            course = Course.objects.get(pk=request.data['course'])

            if SeshRequest.objects.filter(student=student, status=0, course=course).count() > 0:
                return Response("You cannot have more than one open request per class")

            discount = None
            if request.data.get('discount', False):
                discount = Discount.objects.get(pk=request.data['discount'])
            expiration_time = dateparse.parse_datetime(request.data['expiration_time'])
            school = request.user.school
            sesh_comp = Constant.objects.get(school_id=school.pk).sesh_comp

            available_blocks = request.data.get('available_blocks', None)
            description = request.data.get('description', 0)
            est_time = int(request.data.get('est_time', 0))

            sesh_request = SeshRequest.objects.create(expiration_time=expiration_time, available_blocks=available_blocks, description=description, est_time=est_time, discount=discount, sesh_comp=sesh_comp, student=student, course=course, num_people=int(request.data['num_people']), school=school, hourly_rate=Decimal(request.data['hourly_rate']))        

            if 'tutor' in request.data:
                sesh_request.tutor = Tutor.objects.get(pk=request.data['tutor'])
                sesh_request.save()
                # notify the selected tutor
                sesh_request.send_direct_request_notification()
            else:
                sesh_request.save()
                # notify all eligible tutors
                sesh_request.send_request_notification()

            # remove pending timeout emails

            # eventually: post to slack

            return Response(SeshRequestSerializer(sesh_request).data)

        except Discount.DoesNotExist:
            raise exceptions.NotFound("Discount not found")
        except Course.DoesNotExist:
            raise exceptions.NotFound("Course not found")
        except Student.DoesNotExist:
            raise exceptions.NotFound("Student not found")
        except Tutor.DoesNotExist:
            raise exceptions.NotFound("Tutor not found")

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
        sesh_request.status = 3
        sesh_request.save()
        sesh_request.send_cancelled_request_notification()
        return Response({"message": "Request cancelled"})

    @detail_route(methods=['post'])
    def accept(self, request, pk=None):
        '''
        Tutor accepts a direct request
        '''
        from apps.chatroom.models import Chatroom

        sesh_request = self.get_object()
        if not sesh_request.tutor or sesh_request.tutor != request.user.tutor or sesh_request.status != 0:
            return Response("Tutor cannot respond to this request")
        sesh_request.status = 1
        sesh_request.save()
        name = sesh_request.course.get_readable_name() + " Sesh"
        desc = sesh_request.tutor.user.readable_name + " tutoring " + sesh_request.student.user.readable_name + " in " + sesh_request.course.get_readable_name()
        chatroom = Chatroom.objects.create(name=name, description=desc)
        sesh = OpenSesh.objects.create(past_request=sesh_request, tutor=sesh_request.tutor, student=sesh_request.student, chatroom=chatroom)
        sesh_request.send_tutor_accepted_notification(sesh)

        return Response(OpenSeshSerializer(sesh).data)

    @detail_route(methods=['post'])
    def reject(self, request, pk=None):
        '''
        Tutor rejects a direct request
        '''
        sesh_request = self.get_object()
        if not sesh_request.tutor or sesh_request.tutor != request.user.tutor or sesh_request.status != 0:
            return Response("Tutor cannot respond to this request")
        sesh_request.status = 4
        sesh_request.save()
        sesh_request.send_tutor_rejected_notification()

        return Response(SeshRequestSerializer(sesh_request).data)


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

        announcement_type = AnnouncementType.objects.get(identifier="USER_SET_LOCATION")
        announcement = Announcement.objects.create(chatroom=open_sesh.chatroom, user=user, announcement_type=announcement_type)

        activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
        activity = ChatroomActivity.objects.create(chatroom=open_sesh.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)

        open_sesh.send_set_location_notification(activity)

        return Response(ChatroomActivitySerializer(activity, context={'request': request}).data)

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

        announcement_type = AnnouncementType.objects.get(identifier="USER_SET_TIME")
        announcement = Announcement.objects.create(chatroom=open_sesh.chatroom, user=user, announcement_type=announcement_type)

        activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
        activity = ChatroomActivity.objects.create(chatroom=open_sesh.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)

        open_sesh.send_set_time_notification(activity)

        return Response(ChatroomActivitySerializer(activity, context={'request': request}).data)


class PastBidViewSet(viewsets.ModelViewSet):
    queryset = PastBid.objects.all()
    serializer_class = PastBidSerializer


class PastSeshViewSet(viewsets.ModelViewSet):
    queryset = PastSesh.objects.all()
    serializer_class = PastSeshSerializer


class ReportedProblemViewSet(viewsets.ModelViewSet):
    queryset = ReportedProblem.objects.all()
    serializer_class = ReportedProblemSerializer
