from apps.tutoring.models import OpenBid, SeshRequest, OpenSesh, PastBid, PastSesh, ReportedProblem
from rest_framework import viewsets
from datetime import datetime, timedelta
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
import stripe
from sesh import settings
from sesh.mandrill_utils import EmailManager
import locale

locale.setlocale(locale.LC_ALL, '')
stripe.api_key = settings.STRIPE_API_KEY
logger = logging.getLogger(__name__)


class OpenBidViewSet(viewsets.ModelViewSet):
    queryset = OpenBid.objects.all()
    serializer_class = OpenBidSerializer


class SeshRequestViewSet(viewsets.ModelViewSet):
    queryset = SeshRequest.objects.all()
    serializer_class = SeshRequestSerializer
    permission_classes = [IsAuthenticated]

    @detail_route(methods=['post'])
    def edit(self, request, pk=None):
        user = request.user
        sesh_request = self.get_object()

        if sesh_request.student != user.student:
            return Response({"detail": "Student cannot edit this request"}, 405)

        if sesh_request.status > 1:
            return Response({"detail": "Student cannot edit this request"}, 405)

        num_people = request.data.get('num_people', None)
        description = request.data.get('description', None)
        location_notes = request.data.get('location_notes', None)
        est_time = request.data.get('est_time', None)

        if num_people is not None:
            sesh_request.num_people = num_people
        if description is not None:
            sesh_request.description = description
        if location_notes is not None:
            sesh_request.location_notes = location_notes
        if est_time is not None:
            sesh_request.est_time = est_time
        if 'available_blocks' in request.data:
            sesh_request.available_blocks = json.dumps(request.data['available_blocks'])

        if sesh_request.status == 0 and 'available_blocks' in request.data:
            # calculate new expiration_time
            jsonArr = request.data.get('available_blocks')
            last_end_time = datetime.now()
            for block in jsonArr:
                end_time = dateparse.parse_datetime(block['end_time'])
                if end_time > last_end_time:
                    last_end_time = end_time

            sesh_request.expiration_time = last_end_time - timedelta(minutes=15)

        sesh_request.save()

        # for now only notifications in sesh
        if sesh_request.status == 1:
            open_sesh = OpenSesh.objects.get(past_request=sesh_request)
            announcement_type = AnnouncementType.objects.get(identifier="USER_EDITED_SESH")
            announcement = Announcement.objects.create(chatroom=open_sesh.chatroom, user=user, announcement_type=announcement_type)
            activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
            activity = ChatroomActivity.objects.create(chatroom=open_sesh.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)

            open_sesh.send_sesh_edited_notification(activity, request)

        return Response(SeshEditableRequestSerializer(sesh_request, context={'request': request}).data)

    @list_route(methods=['post'])
    def get_available_jobs(self, request):
        '''
        get available jobs for the requesting tutor
        '''
        from apps.tutor.models import TutorCourse

        # TODO add departments

        user = request.user

        courses = TutorCourse.objects.filter(tutor=user.tutor)
        requests = SeshRequest.objects.filter(status=0, tutor=None, course__in=courses.values('course_id')).exclude(student=user.student)

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

            school = request.user.school
            sesh_comp = Constant.objects.get(school_id=school.pk).sesh_comp
            available_blocks = None
            if request.data.get('available_blocks', False):
                available_blocks = json.dumps(request.data['available_blocks'])

            # calculate new expiration_time
            jsonArr = request.data.get('available_blocks')
            last_end_time = datetime.now()
            for block in jsonArr:
                end_time = dateparse.parse_datetime(block['end_time'])
                if end_time > last_end_time:
                    last_end_time = end_time

            sesh_request.expiration_time = last_end_time - timedelta(minutes=15)

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

            # TODO remove pending timeout emails

            # TODO post to slack

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

        user = request.user
        open_sesh = self.get_object()
        cancellation_reason = request.data.get('cancellation_reason', None)
        constants = Constant.objects.get(school_id=user.school.pk)

        if open_sesh.has_started:
            return Response({"detail": "Sesh cannot be cancelled once it has started"}, 405)

        if open_sesh.student == user.student:
            # fee_enabled = user.device is not None and user.device.type == 'ios' and user.device.app_version >= 11
            fee_enabled = True
            has_activity = ChatroomActivity.objects.filter(chatroom=open_sesh.chatroom).count() > 0

            tutor_percentage = 1.0 - float(constants.administrative_percentage)
            past_sesh = PastSesh.objects.create(past_request=open_sesh.past_request, tutor=open_sesh.tutor, student=open_sesh.student, start_time=open_sesh.start_time, end_time=datetime.now(), tutor_percentage=tutor_percentage, student_cancelled=True, tutor_cancelled=False, was_cancelled=True, cancellation_reason=cancellation_reason, set_time=open_sesh.set_time, chatroom=open_sesh.chatroom)

            # archive the chatroom and delete open_sesh
            open_sesh.chatroom.is_past = True
            open_sesh.chatroom.save()
            open_sesh.delete()

            if fee_enabled and has_activity and open_sesh.set_time is not None:
                timeout = constants.sesh_cancellation_timeout_minutes
                date_diff = open_sesh.set_time - datetime.now()

                if date_diff.total_seconds()/60.0 < timeout:
                    cancellation_fee = float(constants.late_cancellation_fee)
                    # TODO charge function should be more like end_sesh and pull from credits
                    past_sesh.charge_student(cancellation_fee)

                    past_sesh.cancellation_charge = cancellation_fee
                    past_sesh.tutor.credits = float(past_sesh.tutor.credits) + (cancellation_fee * tutor_percentage)
                    past_sesh.tutor.save()

            past_sesh.send_student_cancelled_notification()
            past_sesh.save()

        elif open_sesh.tutor == user.tutor:

            tutor_percentage = 1.0 - constants.administrative_percentage
            past_sesh = PastSesh.objects.create(
                past_request=open_sesh.past_request,
                tutor=open_sesh.tutor,
                student=open_sesh.student,
                start_time=open_sesh.start_time,
                end_time=datetime.now(),
                tutor_percentage=tutor_percentage,
                student_cancelled=False,
                tutor_cancelled=True,
                was_cancelled=True,
                cancellation_reason=cancellation_reason,
                set_time=open_sesh.set_time,
                chatroom=open_sesh.chatroom
            )

            # notify student of cancellation
            past_sesh.send_tutor_cancelled_notification()

            # archive the chatroom and delete open_sesh
            open_sesh.chatroom.is_past = True
            open_sesh.chatroom.save()
            open_sesh.delete()

        else:
            return Response({"detail": "User is not part of this Sesh"}, 405)

        return Response()

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def start(self, request, pk=None):
        '''
        Start the sesh, can only be called by the tutor
        '''
        user = request.user
        open_sesh = self.get_object()

        if user.tutor != open_sesh.tutor:
            return Response({"detail": "User does not own this Sesh"}, 405)

        if open_sesh.has_started:
            return Response({"detail": "This Sesh has already started"}, 405)

        open_sesh.has_started = True
        open_sesh.start_time = datetime.now()
        open_sesh.save()

        # update states
        open_sesh.student.user.update_sesh_state('SeshStateInSesh', {"sesh_id": open_sesh.pk, "start_time": str(open_sesh.start_time)})
        open_sesh.tutor.user.update_sesh_state('SeshStateInSesh', {"sesh_id": open_sesh.pk, "start_time": str(open_sesh.start_time)})

        open_sesh.send_has_started_notification()

        return Response()

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def end(self, request, pk=None):
        '''
        End an ongoing Sesh
        '''
        from apps.university.models import Constant, DiscountUse
        from apps.transaction.models import OutstandingCharge

        user = request.user
        open_sesh = self.get_object()
        constants = Constant.objects.get(school_id=user.school.pk)

        if user.tutor != open_sesh.tutor:
            return Response({"detail": "User does not own this Sesh"}, 405)

        if not open_sesh.has_started:
            return Response({"detail": "This Sesh has not started"}, 405)

        # TODO: check for promo completion

        # move sesh to past
        past_sesh = PastSesh.objects.create(
            past_request=open_sesh.past_request,
            tutor=open_sesh.tutor,
            student=open_sesh.student,
            start_time=open_sesh.start_time,
            end_time=datetime.now(),
            set_time=open_sesh.set_time,
            chatroom=open_sesh.chatroom
            )
        # open_sesh.delete()

        tutor = past_sesh.tutor

        # calculate price and charge
        past_request = past_sesh.past_request
        num_guests = past_request.num_people - 1
        tutor_percentage = 1.0 - float(constants.administrative_percentage)
        rate = float(past_request.hourly_rate) + (num_guests * float(constants.additional_student_fee))
        duration = max(past_sesh.duration() * 60, constants.minimum_sesh_duration)/60.0
        price = past_sesh.get_cost()

        comp = duration * float(past_request.sesh_comp)

        past_sesh.charge_student(price)

        # handle tutor payment
        tutor_payment = (price + comp) * tutor_percentage
        if tutor.num_seshes == 0 and tutor_payment < constants.first_tutor_rate:
            tutor_payment = constants.first_tutor_rate
            tutor_percentage = 1.0
        elif tutor_payment < constants.tutor_min:
            tutor_payment = constants.tutor_min
            tutor_percentage = 1.0

        # make sure tutor doesn't have outstanding charges
        charges = OutstandingCharge.objects.filter(user=past_sesh.tutor.user, resolved=False)
        for c in charges:
            amount = float(c.amount_owed) - float(c.amount_payed)
            if tutor_payment >= amount:
                tutor_payment = tutor_payment - amount
                c.resolved = True
                c.save()
            else:
                c.amount_payed = c.amount_payed + tutor_payment
                c.save()
                tutor_payment = 0.0
                break

        tutor.credits = float(tutor.credits) + tutor_payment
        tutor.save()
        past_sesh.tutor_earnings = tutor_payment
        past_sesh.save()

        # send tutor review email (TODO separate one if direct request?)
        # TODO update tutor review email without admin fee stuff? talk to Neil about new/updated templates
        base_rate_min = (float(past_request.hourly_rate) + float(past_request.sesh_comp))/60.0 * tutor_percentage
        student_rate_min = num_guests * float(constants.additional_student_fee)/60.0 * tutor_percentage
        total_rate_min = base_rate_min + student_rate_min
        duration_minutes = "{} min".format(int(duration * 60))
        if (duration < 30):
            duration_minutes = "< 30 min"
        merge_vars = {
            'NAME': past_sesh.student.user.readable_name,
            'COURSE': past_request.course.get_readable_name(),
            'ASSIGNMENT': past_request.description if past_request.description is not None else "",
            'TIME': duration_minutes,
            'STUDENTS': past_request.num_people,
            'BASE_RATE_PER_MIN': locale.currency(base_rate_min),
            'ADDITIONAL_STUDENT_PER_MIN': locale.currency(student_rate_min),
            'TOTAL_RATE_MIN': locale.currency(total_rate_min),
            'ADMINISTRATIVE_FEE': float(constants.administrative_percentage)*100,
            'ADMINISTRATIVE_TOTAL': '-%s' % locale.currency(past_sesh.get_cost() * float(constants.administrative_percentage)),
            'TOTAL_EARNED': locale.currency(tutor_payment),  # TODO add referral bonus here
            'PRICE': locale.currency(past_sesh.get_cost()),
            'FIRST_NAME': tutor.user.readable_name,
            'SCHOOL': past_request.school.name
            # TODO add 'REFERRAL_BONUS':
        }

        if tutor.num_seshes == 0:
            EmailManager.send_email(EmailManager.TUTOR_FIRST_SESH_RECEIPT, merge_vars, tutor.user.email, tutor.user.readable_name, None)
        else:
            EmailManager.send_email(EmailManager.REVIEW_SESH_TUTOR, merge_vars, tutor.user.email, tutor.user.readable_name, None)

        # archive chatroom
        past_sesh.chatroom.is_past = True
        past_sesh.chatroom.save()

        # increment num_seshes for tutor
        tutor.num_seshes = tutor.num_seshes + 1
        tutor.save()

        # TODO award bonus points if applicable

        # update states
        past_sesh.student.user.update_sesh_state('SeshStateNone')
        tutor.user.update_sesh_state('SeshStateNone')

        # clear old notifications, send REVIEW and REFRESH
        past_sesh.send_has_ended_notifications()

        # TODO: post to slack

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

        announcement_type = AnnouncementType.objects.get(identifier="USER_EDITED_SESH")
        announcement = Announcement.objects.create(chatroom=open_sesh.chatroom, user=user, announcement_type=announcement_type)

        activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
        activity = ChatroomActivity.objects.create(chatroom=open_sesh.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)

        open_sesh.send_sesh_edited_notification(activity, request)

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
