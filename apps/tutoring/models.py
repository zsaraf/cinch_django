# -*- coding: utf-8 -*-

from django.db import models
from apps.chatroom.models import ChatroomMember
from datetime import datetime, timedelta
from apps.notification.models import OpenNotification, NotificationType, PastNotification
from apps.university.models import Constant
from decimal import *
from sesh.mandrill_utils import EmailManager
from sesh import settings
import locale
import stripe

locale.setlocale(locale.LC_ALL, '')
stripe.api_key = settings.STRIPE_API_KEY


class OpenBid(models.Model):
    request_id = models.IntegerField()
    tutor = models.ForeignKey('tutor.Tutor')
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'open_bids'


class SeshRequest(models.Model):
    tutor = models.ForeignKey('tutor.Tutor', blank=True, null=True)
    student = models.ForeignKey('student.Student')
    school = models.ForeignKey('university.School')
    course = models.ForeignKey('university.Course', db_column='class_id')
    description = models.CharField(max_length=100, blank=True, null=True)
    processing = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    est_time = models.IntegerField(blank=True, null=True)
    num_people = models.IntegerField(default=1)
    hourly_rate = models.DecimalField(max_digits=19, decimal_places=4)
    expiration_time = models.DateTimeField(blank=True, null=True)
    is_instant = models.IntegerField(default=0)
    available_blocks = models.TextField(blank=True, null=True)
    location_notes = models.CharField(max_length=32, blank=True, null=True)
    discount = models.ForeignKey('university.Discount', blank=True, null=True)
    sesh_comp = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    status = models.IntegerField(default=0)
    has_seen = models.BooleanField(default=False)
    cancellation_reason = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'request'

    def get_estimated_wage(self):
        '''
        Get estimated wage for a request
        '''
        tutor_rate = self.adjusted_hourly_rate()
        return tutor_rate * Decimal(int(self.est_time) / 60.0)

    def adjusted_hourly_rate(self):
        constants = Constant.objects.get(school_id=self.school.pk)
        additional_student_fee = (int(self.num_people) - 1) * constants.additional_student_fee
        tutor_rate = (self.hourly_rate + self.sesh_comp + additional_student_fee) * Decimal(1.0 - constants.administrative_percentage)
        return tutor_rate

    def send_tutor_rejected_notification(self):
        '''
        Sends a notification to the student that the tutor rejected the request
        '''
        merge_vars = {
            "TUTOR_NAME": self.tutor.user.readable_name,
            "COURSE_NAME": self.course.get_readable_name()
        }
        data = {
            "request_id": self.pk
        }
        notification_type = NotificationType.objects.get(identifier="DIRECT_REQUEST_REJECTED")
        OpenNotification.objects.create(self.student.user, notification_type, data, merge_vars, None)

    def clear_notifications(self):
        '''
        After a request has ended, clear old notifications for all users
        '''
        import json

        new_request_notification_type = NotificationType.objects.get(identifier="NEW_REQUEST")

        notifications = OpenNotification.objects.filter(notification_type=new_request_notification_type)
        for n in notifications:
            json_arr = json.loads(n.data)
            request_id = json_arr.get('request_id')
            if request_id == self.pk:
                PastNotification.objects.create(data=n.data, user_id=n.user.pk, notification_type=n.notification_type, notification_vars=n.notification_vars, has_sent=n.has_sent, send_time=n.send_time)
                OpenNotification.objects.get(pk=n.pk).delete()

    def send_request_notification(self):
        '''
        Sends a notification to all eligible tutors that job is available
        '''
        from apps.tutor.models import TutorCourse, TutorDepartment
        import locale

        locale.setlocale(locale.LC_ALL, '')

        merge_vars = {
            "CLOCK_SAYING": "🕒",
            "RATE_SAYING": "💵",
            "EST_TIME": self.est_time,
            "HOURLY_RATE": locale.currency(self.hourly_rate),
            "ESTIMATED_WAGE": locale.currency(self.get_estimated_wage()),
            "COURSE_NAME": self.course.get_readable_name()
        }
        data = {
            'request_id': self.id
        }
        tutor_courses = TutorCourse.objects.filter(course=self.course)
        tutors = [tc.tutor for tc in tutor_courses]
        tutor_departments = TutorDepartment.objects.filter(department=self.course.department).exclude(tutor_id__in=tutor_courses.values('tutor_id'))
        tutors.extend([td.tutor for td in tutor_departments])

        notification_type = NotificationType.objects.get(identifier="NEW_REQUEST")
        for tutor in tutors:
            OpenNotification.objects.create(tutor.user, notification_type, data, merge_vars, None)

    def send_direct_request_notification(self):
        '''
        Sends a notification to the tutor that job is available
        '''
        from serializers import NotificationSeshRequestSerializer

        merge_vars = {
            "STUDENT_NAME": self.student.user.readable_name,
            "COURSE_NAME": self.course.get_readable_name(),
            "HOURLY_RATE": locale.currency(self.adjusted_hourly_rate())
        }
        data = {
            "request": NotificationSeshRequestSerializer(self).data
        }
        notification_type = NotificationType.objects.get(identifier="NEW_DIRECT_REQUEST")
        OpenNotification.objects.create(self.tutor.user, notification_type, data, merge_vars, None)

    def send_tutor_accepted_notification(self, sesh):
        '''
        Sends a notification to the student that the request was accepted
        '''
        merge_vars = {
            "TUTOR_NAME": self.tutor.user.readable_name,
            "COURSE_NAME": self.course.get_readable_name()
        }
        data = {
            "sesh_id": sesh.pk
        }
        notification_type = NotificationType.objects.get(identifier="DIRECT_REQUEST_ACCEPTED")
        OpenNotification.objects.create(self.student.user, notification_type, data, merge_vars, None)


class OpenSesh(models.Model):
    past_request = models.OneToOneField('SeshRequest')
    tutor = models.ForeignKey('tutor.Tutor')
    timestamp = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(blank=True, null=True)
    has_started = models.IntegerField(default=0)
    student = models.ForeignKey('student.Student')
    set_time = models.DateTimeField(blank=True, null=True)
    is_instant = models.IntegerField(default=0)
    location_notes = models.CharField(max_length=32)
    has_received_start_time_approaching_reminder = models.IntegerField(blank=True, null=True)
    has_received_set_start_time_initial_reminder = models.IntegerField(blank=True, null=True)
    chatroom = models.ForeignKey('chatroom.Chatroom', blank=True, null=True)

    def send_sesh_edited_notification(self, request, sesh_id):
        '''
        Sends notification that sesh's request was edited
        '''
        merge_vars = {
            "STUDENT_NAME": self.student.user.readable_name
        }

        data = {
            "request_id": self.past_request.id,
            "chatroom_id": self.chatroom.id
        }
        notification_type = NotificationType.objects.get(identifier="SESH_EDITED")
        OpenNotification.objects.create(self.tutor.user, notification_type, data, merge_vars, None)

    def send_has_started_notification(self):
        '''
        Sends a notification to student that the sesh has started
        '''
        data = {
            'chatroom_id': self.chatroom.id
        }
        merge_vars = {
            "TUTOR_NAME": self.tutor.user.readable_name
        }
        notification_type = NotificationType.objects.get(identifier="SESH_STARTED_STUDENT")
        OpenNotification.objects.create(self.student.user, notification_type, data, merge_vars, None)

    def clear_approaching_notifications(self):
        '''
        Clears old SESH_APPROACHING notifications when new time is set
        '''
        search_str = "\"chatroom_id\": " + str(self.chatroom.id)
        student_type = NotificationType.objects.get(identifier='SESH_APPROACHING_STUDENT')
        tutor_type = NotificationType.objects.get(identifier='SESH_APPROACHING_TUTOR')

        OpenNotification.objects.filter(user=self.student.user, notification_type=student_type, data__icontains=search_str).delete()
        OpenNotification.objects.filter(user=self.tutor.user, notification_type=tutor_type, data__icontains=search_str).delete()

    def send_set_time_notification(self, chatroom_activity, request):
        '''
        Sends a notification to the chatroom members
        '''

        # clear out other set_time requests
        # search_str = "\"chatroom\": " + str(self.chatroom_id)
        notification_type = NotificationType.objects.get(identifier="SET_TIME_UPDATED")
        # existing_notifications = OpenNotification.objects.filter(user__in=[self.student.user, self.tutor.user], data__icontains=search_str, notification_type=notification_type)
        # for n in existing_notifications:
        #     PastNotification.objects.create(data=n.data, user_id=n.user.pk, notification_type=n.notification_type, notification_vars=n.notification_vars, has_sent=n.has_sent, send_time=n.send_time)
        #     OpenNotification.objects.get(pk=n.pk).delete()

        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom, is_past=False).exclude(user=self.tutor.user)
        merge_vars = {
            "TUTOR_NAME": self.tutor.user.readable_name,
            "SET_TIME": self.set_time
        }
        data = chatroom_activity.get_pn_data(request)
        data['set_time'] = self.set_time

        for cm in chatroom_members:
            if cm.notifications_enabled:
                OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

        # create delayed notification for 30 minute reminder
        reminder_time = datetime.strptime(self.set_time, '%Y-%m-%d %H:%M:%S') - timedelta(minutes=30)
        student_type = NotificationType.objects.get(identifier='SESH_APPROACHING_STUDENT')
        OpenNotification.objects.create(self.student.user, student_type, data, None, reminder_time)
        merge_vars = {
            'START_TIME': self.set_time,
            'STUDENT_NAME': self.student.user.first_name
        }
        tutor_type = NotificationType.objects.get(identifier='SESH_APPROACHING_TUTOR')
        OpenNotification.objects.create(self.tutor.user, tutor_type, data, merge_vars, reminder_time)

    class Meta:
        managed = False
        db_table = 'open_seshes'


class PastBid(models.Model):
    past_request = models.ForeignKey('SeshRequest')
    tutor = models.ForeignKey('tutor.Tutor')
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'past_bids'


class PastSesh(models.Model):
    past_request = models.OneToOneField('SeshRequest')
    tutor = models.ForeignKey('tutor.Tutor')
    student = models.ForeignKey('student.Student', blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField()
    student_credits_applied = models.DecimalField(default=0, max_digits=19, decimal_places=4)
    tutor_credits_applied = models.DecimalField(default=0, max_digits=19, decimal_places=4)
    sesh_credits_applied = models.DecimalField(default=0, max_digits=19, decimal_places=4)
    rating_1 = models.IntegerField(default=5)
    rating_2 = models.IntegerField(default=5)
    rating_3 = models.IntegerField(default=5)
    charge_id = models.CharField(max_length=100)
    tutor_percentage = models.FloatField(default=1.0)
    tutor_earnings = models.DecimalField(default=0, max_digits=19, decimal_places=4)
    student_cancelled = models.BooleanField(default=False)
    tutor_cancelled = models.BooleanField(default=False)
    was_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.CharField(default=None, max_length=30, blank=True, null=True)
    cancellation_charge = models.DecimalField(default=0, max_digits=19, decimal_places=4)
    set_time = models.DateTimeField(blank=True, null=True)
    chatroom = models.ForeignKey('chatroom.Chatroom', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'past_seshes'

    def get_cost(self):
        from apps.university.models import Constant
        if self.was_cancelled:
            return self.cancellation_charge

        constants = Constant.objects.get(school_id=self.student.user.school.id)
        past_request = self.past_request
        duration = max(self.duration() * 60, constants.minimum_sesh_duration)/60.0
        num_guests = past_request.num_people - 1
        rate = float(past_request.hourly_rate) + (num_guests * float(constants.additional_student_fee))
        price = rate * float(duration)
        return price

    def send_student_review_email(self, brand, last_four):
        from apps.university.models import Constant
        constants = Constant.objects.get(school_id=self.student.user.school.id)

        base_rate_min = float(self.past_request.hourly_rate)/60.0
        student_rate_min = (self.past_request.num_people - 1) * float(constants.additional_student_fee)/60.0
        total_rate_min = base_rate_min + student_rate_min
        cost = self.get_cost()

        duration = max(self.duration() * 60, constants.minimum_sesh_duration)/60.0
        duration_minutes = "{} min".format(int(duration * 60))
        if (duration < 30):
            duration_minutes = "< 30 min"

        credits_applied = self.sesh_credits_applied + self.student_credits_applied + self.tutor_credits_applied
        charge_amount = cost - float(credits_applied)
        if not brand and not last_four:
            if charge_amount > 0:
                charge_amount = 0
                card = "none (charge &lt; $0.50)"
            else:
                card = "none"
        else:
            card = "{} - {}".format(brand, last_four)

        merge_vars = {
            'NAME': self.tutor.user.readable_name,
            'COURSE': self.past_request.course.get_readable_name(),
            'ASSIGNMENT': self.past_request.description if self.past_request.description is not None else "",
            'TIME': duration_minutes,
            'STUDENTS': self.past_request.num_people,
            'BASE_RATE_PER_MIN': locale.currency(base_rate_min),
            'ADDITIONAL_STUDENT_PER_MIN': locale.currency(student_rate_min),
            'TOTAL_RATE_MIN': locale.currency(total_rate_min),
            'TOTAL_PRICE': locale.currency(cost),
            'CREDIT_APPLIED': credits_applied,
            'CARD_CHARGE_AMOUNT': locale.currency(charge_amount),
            'CARD': card,
            'PRICE': locale.currency(cost),
        }

        if self.was_cancelled:
            merge_vars['CANCELLATION_FEE'] = self.cancellation_charge
            EmailManager.send_email(EmailManager.STUDENT_CANCELLATION_FEE_RECEIPT, merge_vars, self.student.user.email, self.student.user.readable_name, None)
        else:
            EmailManager.send_email(EmailManager.REVIEW_SESH_STUDENT, merge_vars, self.student.user.email, self.student.user.readable_name, None)

    def charge_student(self, price):
        remainder = price
        past_request = self.past_request
        # apply sesh credits
        if past_request.discount is not None:
            remainder = max(price - past_request.discount.credit_amount, 0)
            DiscountUse.objects.create(user=self.student.user, discount=self.discount)

        sesh_credits_applied = price - remainder
        self.sesh_credits_applied = sesh_credits_applied

        # apply student credits
        curr_credits = float(self.student.credits)
        new_credits = curr_credits - remainder
        if curr_credits < remainder:
            new_credits = 0.0
            remainder = remainder - curr_credits
        else:
            remainder = 0.0
        self.student.credits = new_credits
        self.student.save()

        # TODO if student credits depleted, email past credit purchasers

        student_credits_applied = price - sesh_credits_applied - remainder
        self.student_credits_applied = student_credits_applied
        self.save()

        # if necessary, pull from tutor credits
        if remainder > 0:
            student_tutor = self.student.user.tutor
            curr_credits = float(student_tutor.credits)
            new_credits = curr_credits - remainder
            final_remainder = 0.0
            if curr_credits < remainder:
                new_credits = 0.0
                final_remainder = remainder - curr_credits
            student_tutor.credits = new_credits
            student_tutor.save()

            self.tutor_credits_applied = price - sesh_credits_applied - student_credits_applied - final_remainder
            self.save()

            # if more that 50 cents remaining after all credits, charge their card
            if final_remainder > 0.5:
                charge_amount = int(final_remainder * 100)
                charge_object = self.stripe_charge_student(charge_amount)

                if charge_object is not None:
                    self.charge_id = charge_object[0]
                    self.save()
                    self.send_student_review_email(charge_object[1], charge_object[2])

            else:
                # got what we needed from credits, email them receipt
                self.send_student_review_email("", "")
        else:
            # got what we needed from credits, email them receipt
            self.send_student_review_email("", "")

    def stripe_charge_student(self, amount):
        from apps.transaction.models import OutstandingCharge

        user = self.student.user

        if user.stripe_customer_id is None:
            ou = OutstandingCharge.objects.create(
                user=self.student.user,
                past_sesh=self,
                amount_owed=amount/100.0,
                code='no_payment_card'
            )
            ou.email_user("You do not have any payment cards.")
            return None

        try:
            cards = stripe.Customer.retrieve(user.stripe_customer_id).sources.all(limit=5, object='card')
            if len(cards) == 0:
                ou = OutstandingCharge.objects.create(
                    user=self.student.user,
                    past_sesh=self,
                    amount_owed=amount/100.0,
                    code='no_payment_card'
                )
                ou.email_user("You do not have any payment cards.")
                return None

            charge = stripe.Charge.create(
                amount=amount,
                currency='usd',
                customer=user.stripe_customer_id,
                statement_descriptor='Sesh Tutoring',
                description='Thank you for choosing Sesh!'
            )

            brand = charge.source.brand
            last_four = charge.source.last4

            return (charge.id, brand, last_four)

        except stripe.error.CardError, e:
            body = e.json_body
            err = body['error']
            code = err['code']

            ou = OutstandingCharge.objects.create(
                user=self.student.user,
                past_sesh=self,
                amount_owed=amount/100.0,
                code=code
            )
            ou.email_user(err['message'])
            return None

        except stripe.error.StripeError, e:
            body = e.json_body
            err = body['error']
            code = err['code']

            ou = OutstandingCharge.objects.create(
                user=self.student.user,
                past_sesh=self,
                amount_owed=amount/100.0,
                code=code
            )
            ou.email_user(err['message'])
            return None

        except Exception, e:
            # TODO handle exception
            return None

    def send_tutor_cancelled_notification(self):
        '''
        Sends a notification to student that tutor has cancelled
        '''
        OpenNotification.objects.clear_by_user_and_chatroom(self.tutor.user, self.chatroom)
        OpenNotification.objects.clear_by_user_and_chatroom(self.student.user, self.chatroom)

        data = {
            "past_sesh_id": self.pk
        }

        merge_vars = {
            "TUTOR_NAME": self.tutor.user.readable_name
        }
        notification_type = NotificationType.objects.get(identifier="SESH_CANCELLED_STUDENT")
        OpenNotification.objects.create(self.student.user, notification_type, data, merge_vars, None)

    def send_student_cancelled_notification(self):
        '''
        Sends a notification to tutor that student has cancelled
        '''
        OpenNotification.objects.clear_by_user_and_chatroom(self.tutor.user, self.chatroom)
        OpenNotification.objects.clear_by_user_and_chatroom(self.student.user, self.chatroom)

        data = {
            "past_sesh_id": self.pk
        }

        merge_vars = {
            "STUDENT_NAME": self.student.user.readable_name
        }
        notification_type = NotificationType.objects.get(identifier="SESH_CANCELLED_TUTOR")
        OpenNotification.objects.create(self.tutor.user, notification_type, data, merge_vars, None)

    def send_has_ended_notifications(self):
        '''
        Clear existing notifications, sends a notifications to review sesh and refresh
        '''
        OpenNotification.objects.clear_by_user_and_chatroom(self.tutor.user, self.chatroom)
        OpenNotification.objects.clear_by_user_and_chatroom(self.student.user, self.chatroom)

        data = {
            "past_sesh_id": self.pk
        }
        notification_type = NotificationType.objects.get(identifier="SESH_REVIEW_STUDENT")
        OpenNotification.objects.create(self.student.user, notification_type, data, None, None)
        notification_type = NotificationType.objects.get(identifier="SESH_REVIEW_TUTOR")
        OpenNotification.objects.create(self.tutor.user, notification_type, data, None, None)

    def duration(self):
        if not self.was_cancelled:
            return (self.end_time - self.start_time).total_seconds()/3600
        else:
            return 0


class ReportedProblem(models.Model):
    past_sesh = models.ForeignKey(PastSesh, blank=True, null=True)
    content = models.CharField(max_length=512, blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'reported_problems'
