from apps.tutoring.models import OpenBid, SeshRequest, OpenSesh, PastBid, PastSesh, ReportedProblem
from rest_framework import viewsets
from datetime import datetime
from rest_framework import exceptions
from apps.tutoring.serializers import *
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from apps.chatroom.models import Announcement, AnnouncementType, ChatroomActivity, ChatroomActivityType, ChatroomActivityTypeManager
from apps.chatroom.serializers import ChatroomActivitySerializer
from rest_framework.response import Response
from decimal import *
from django.utils import dateparse
import json
import logging
logger = logging.getLogger(__name__)


class OpenBidViewSet(viewsets.ModelViewSet):
    queryset = OpenBid.objects.all()
    serializer_class = OpenBidSerializer


class SeshRequestViewSet(viewsets.ModelViewSet):
    queryset = SeshRequest.objects.all()
    serializer_class = SeshRequestSerializer
    permission_classes = [IsAuthenticated]

    @list_route(methods=['post'])
    def get_available_jobs(self, request):
        '''
        get available jobs for the requesting tutor
        '''
        from apps.tutor.models import TutorCourse

        user = request.user

        courses = TutorCourse.objects.filter(tutor=user.tutor)
        requests = SeshRequest.objects.filter(status=0, tutor=None, course__in=courses.values('course_id'))

        return Response(SeshRequestSerializer(requests, many=True).data)

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
            available_blocks = None
            if request.data.get('available_blocks', False):
                available_blocks = json.dumps(request.data['available_blocks'])

            est_time = int(request.data.get('est_time', 0))

            sesh_request = SeshRequest.objects.create(
                expiration_time=expiration_time,
                available_blocks=available_blocks,
                description=request.data.get('description', None),
                est_time=est_time,
                discount=discount,
                sesh_comp=sesh_comp,
                student=student,
                course=course,
                location_notes=request.data.get('location_notes', None),
                num_people=int(request.data['num_people']),
                school=school,
                hourly_rate=Decimal(request.data['hourly_rate'])
            )

            if 'tutor' in request.data and request.data['tutor']:
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
        cancellation_reason = request.data.get("cancellation_reason")
        if request.user.student != sesh_request.student:
            return Response({"detail": "Student cannot cancel this request"}, 405)
        if sesh_request.status > 0:
            return Response({"detail": "It's too late to cancel this request"}, 405)
        sesh_request.status = 3
        sesh_request.cancellation_reason = cancellation_reason
        sesh_request.save()
        sesh_request.clear_notifications()

        return Response()

    @detail_route(methods=['post'])
    def accept(self, request, pk=None):
        '''
        Tutor accepts a direct request
        '''
        from apps.chatroom.models import Chatroom, ChatroomMember

        sesh_request = self.get_object()
        if sesh_request.tutor is None or sesh_request.tutor != request.user.tutor:
            return Response({"detail": "Tutor cannot respond to this request"}, 405)

        if sesh_request.status != 0:
            return Response({"detail": "The student cancelled the request."})

        sesh_request.status = 1
        sesh_request.save()
        name = sesh_request.course.get_readable_name() + " Sesh"
        desc = sesh_request.tutor.user.readable_name + " tutoring " + sesh_request.student.user.readable_name + " in " + sesh_request.course.get_readable_name()
        chatroom = Chatroom.objects.create(name=name, description=desc)
        ChatroomMember.objects.create(
            chatroom=chatroom,
            user=request.user
        )
        ChatroomMember.objects.create(
            chatroom=chatroom,
            user=sesh_request.student.user
        )
        sesh = OpenSesh.objects.create(past_request=sesh_request, tutor=sesh_request.tutor, student=sesh_request.student, chatroom=chatroom)
        sesh_request.send_tutor_accepted_notification(sesh)
        return Response(OpenSeshSerializer(sesh, context={'request': request}).data)

    @detail_route(methods=['post'])
    def reject(self, request, pk=None):
        '''
        Tutor rejects a direct request
        '''
        sesh_request = self.get_object()

        if sesh_request.tutor is None or sesh_request.tutor != request.user.tutor:
            return Response({"detail": "Tutor cannot respond to this request"}, 405)

        if sesh_request.status != 0:
            return Response({"detail": "The student cancelled the request."})

        sesh_request.status = 4
        sesh_request.save()
        sesh_request.send_tutor_rejected_notification()

        return Response()


class OpenSeshViewSet(viewsets.ModelViewSet):
    queryset = OpenSesh.objects.all()
    serializer_class = OpenSeshSerializer

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        '''
        Cancel an open sesh
        '''
        from apps.university.models import Constant
        from apps.account.models import Device
        from apps.notification.models import NotificationType, OpenNotification

        user = request.user
        open_sesh = self.get_object()
        cancellation_reason = request.data.get('cancellation_reason', None)
        constants = Constant.objects.get(school_id=user.school.pk)

        if open_sesh.has_started:
            return Response({"detail": "Sesh cannot be cancelled once it has started"}, 405)

        if open_sesh.student == user.student:
            fee_enabled = user.device is not None and user.device.type == 'ios' and user.device.app_version >= 11
            has_activity = ChatroomActivity.objects.filter(chatroom=open_sesh.chatroom).count() > 0

            if fee_enabled and has_activity and open_sesh.set_time is not None:
                timeout = constants.sesh_cancellation_timeout_minutes
                date_diff = open_sesh.set_time - datetime.now()

                # if date_diff.total_minutes() < timeout:
                #     # charge cancellation fee
            open_sesh.send_student_cancelled_notification()
            tutor_percentage = 1.0 - constants.administrative_percentage
            PastSesh.objects.create(past_request=open_sesh.past_request, tutor=open_sesh.tutor, student=open_sesh.student, start_time=open_sesh.start_time, end_time=datetime.now(), tutor_percentage=tutor_percentage, student_cancelled=True, tutor_cancelled=False, was_cancelled=True, cancellation_reason=cancellation_reason, set_time=open_sesh.set_time, chatroom=open_sesh.chatroom)


        elif open_sesh.tutor == user.tutor:
            # notify student of cancellation
            open_sesh.send_tutor_cancelled_notification()
            tutor_percentage = 1.0 - constants.administrative_percentage
            PastSesh.objects.create(past_request=open_sesh.past_request, tutor=open_sesh.tutor, student=open_sesh.student, start_time=open_sesh.start_time, end_time=datetime.now(), tutor_percentage=tutor_percentage, student_cancelled=False, tutor_cancelled=True, was_cancelled=True, cancellation_reason=cancellation_reason, set_time=open_sesh.set_time, chatroom=open_sesh.chatroom)

        else:
            return Response({"detail": "User is not part of this Sesh"}, 405)

        # archive the chatroom
        open_sesh.chatroom.is_past = True
        open_sesh.chatroom.save()
        open_sesh.delete()

        return Response()

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def start(self, request, pk=None):
        '''
        Start the sesh, can only be called by the tutor
        '''
        from apps.account.models import SeshState
        user = request.user
        open_sesh = self.get_object()

        if user.tutor != open_sesh.tutor:
            return Response({"detail": "User does not own this Sesh"}, 405)

        if open_sesh.has_started:
            return Response({"detail": "This Sesh has already started"}, 405)

        open_sesh.has_started = True
        open_sesh.start_time = datetime.now()
        open_sesh.save()

        in_sesh = SeshState.objects.get(identifier="SeshStateInSesh")
        open_sesh.student.user.sesh_state = in_sesh
        open_sesh.tutor.user.sesh_state = in_sesh

        open_sesh.send_has_started_notification()

        return Response()

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

        open_sesh.send_set_location_notification(activity, request)

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

        open_sesh.send_set_time_notification(activity, request)

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
