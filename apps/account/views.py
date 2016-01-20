from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.university.models import Constant
from django.utils.crypto import get_random_string
import hashlib
import re
from sesh.s3utils import upload_image_to_s3, get_file_from_s3, get_resized_image, delete_image_from_s3
from .models import *
from .serializers import *
from apps.tutor.models import Tutor
from apps.student.models import Student
import logging
logger = logging.getLogger(__name__)


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class DoNotEmailViewSet(viewsets.ModelViewSet):
    queryset = DoNotEmail.objects.all()
    serializer_class = DoNotEmailSerializer


class EmailUserDataViewSet(viewsets.ModelViewSet):
    queryset = EmailUserData.objects.all()
    serializer_class = EmailUserDataSerializer


class PasswordChangeRequestViewSet(viewsets.ModelViewSet):
    queryset = PasswordChangeRequest.objects.all()
    serializer_class = PasswordChangeRequestSerializer


class PastBonusViewSet(viewsets.ModelViewSet):
    queryset = PastBonus.objects.all()
    serializer_class = PastBonusSerializer


class PromoCodeViewSet(viewsets.ModelViewSet):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer


class SeshStateViewSet(viewsets.ModelViewSet):
    queryset = SeshState.objects.all()
    serializer_class = SeshStateSerializer


class TokenViewSet(viewsets.ModelViewSet):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegularInfoSerializer

    @list_route(methods=['post'])
    def toggle_daily_digest(self, request):
        user = request.user
        user.daily_digest_enabled = not user.daily_digest_enabled
        user.save()
        return Response()

    def create(self, request):
        '''
        Create a new user
        '''
        from apps.university.models import School
        from apps.chatroom.models import Chatroom, ChatroomMember, ChatroomActivity, ChatroomActivityType, ChatroomActivityTypeManager, Message
        from apps.chatroom.serializers import WelcomeMessageChatroomActivitySerializer
        from apps.group.models import Conversation, ConversationParticipant
        from apps.notification.models import OpenNotification, NotificationType

        email = request.data.get('email').lower()
        full_name = request.data.get('full_name')
        password = request.data.get('password')
        promo_code = request.data.get('promo_code', None)
        pending_tutor_verification_id = request.data.get('pending_tutor_verification_id', None)
        version_number = float(request.data.get('version_number', 1.0))

        if version_number < 2:
            return Response({"detail": "Download the latest version on the AppStore then try again!"}, 405)

        promo_recipient = None

        try:
            if promo_code is not None and len(promo_code) != 0:
                promo_recipient = User.objects.get(share_code=promo_code.lower())
        except User.DoesNotExist:
            return Response({"detail": "Invalid promo code"}, 405)

        try:
            existing_user = User.objects.get(email=email)
            if existing_user.is_verified:
                return Response({"detail": "An account with that email already exists"}, 405)
            else:
                str_to_hash = 'Eabltf1!' + existing_user.salt + password
                m = hashlib.sha1()
                m.update(str_to_hash)
                hex_dig = m.hexdigest()
                if existing_user.password == hex_dig:
                    return Response()
                else:
                    return Response({"detail": "An account with that email already exists"}, 405)

        except User.DoesNotExist:
            # brand new user

            # validate entries
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return Response({"detail": "Invalid email"}, 405)

            if len(email) > 100:
                return Response({"detail": "Invalid email"}, 405)

            if len(full_name) > 100:
                full_name = full_name[0:99]

            full_name.strip()
            parts = full_name.split(" ")
            if len(parts) < 2:
                return Response({"detail": "Please enter both a first and last name"}, 405)

            if len(password) > 100:
                return Response({"detail": "Your password is too long."}, 405)

            if len(password) < 6:
                return Response({"detail": "The password you entered is too short. It must be at least 6 characters!"}, 405)

            salt = get_random_string(length=25)
            str_to_hash = 'Eabltf1!' + salt + password
            m = hashlib.sha1()
            m.update(str_to_hash)
            hex_dig = m.hexdigest()

            verification_id = get_random_string(length=32)
            is_verified = False

            # assign unique code
            new_user_promo = get_random_string(length=5).lower()
            while True:
                try:
                    User.object.get(share_code=new_user_promo)
                    new_user_promo = get_random_string(length=5).lower()
                except:
                    break

            if pending_tutor_verification_id is not None:
                # check for pending verification stuff and change is_verified if appropriate
                try:
                    PendingTutor.objects.get(email=email, verification_id=pending_tutor_verification_id)
                    is_verified = True
                except:
                    return Response({"detail": "Invalid pending tutor id"}, 405)

            school = School.objects.get_school_from_email(email)
            if not school:
                return Response({"detail": "Sorry, we're not at your school yet!"}, 405)

            state = SeshState.objects.get(identifier='SeshStateNone')
            user = User.objects.create(email=email, password=hex_dig, salt=salt, full_name=full_name, verification_id=verification_id, school=school, sesh_state=state, is_verified=is_verified, share_code=new_user_promo)

            user.send_verification_email()

            # create auto welcome message from team@seshtutoring
            try:
                team_user = User.objects.get(email='team@seshtutoring.com').exclude(id=user.pk)

                name = "The Sesh Team"
                desc = "We're so happy you're here! Any questions?"
                chatroom = Chatroom.objects.create(name=name, description=desc)
                conversation = Conversation.objects.create(chatroom=chatroom)
                ConversationParticipant.objects.create(user=user, conversation=conversation)
                ConversationParticipant.objects.create(user=team_user, conversation=conversation)
                ChatroomMember.objects.create(user=user, chatroom=chatroom)
                team_member = ChatroomMember.objects.create(user=team_user, chatroom=chatroom)
                text = "Welcome to the new and improved Sesh! Feel free to message us at any time to ask questions, give feedback, or just say hi. We're always here to improve your experience and make sure you get the most out of our platform."
                message = Message.objects.create(message=text, chatroom=chatroom, chatroom_member=team_member)
                activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.MESSAGE)
                activity = ChatroomActivity.objects.create(chatroom=chatroom, chatroom_activity_type=activity_type, activity_id=message.pk)

                merge_vars = {
                    "NAME": team_user.full_name,
                    "MESSAGE": text
                }
                data = {
                    "chatroom_activity": WelcomeMessageChatroomActivitySerializer(activity).data,
                }
                notification_type = NotificationType.objects.get(identifier="NEW_MESSAGE")
                OpenNotification.objects.create(user, notification_type, data, merge_vars, None)
            except User.DoesNotExist:
                pass

            if promo_code is not None and promo_recipient is not None:
                constants = Constant.objects.get(school_id=promo_recipient.school.pk)
                promo_type = PromoType.objects.get(identifier='user_to_user_share')
                SharePromo.objects.create(new_user=user, old_user=promo_recipient, promo_type=promo_type, amount=getattr(constants, promo_type.award_constant_name))

            return Response()

    @list_route(methods=['POST'])
    def update_user_info(self, request):
        user = request.user
        bio = request.data.get('bio', None)
        major = request.data.get('major', None)
        class_year = request.data.get('class_year', None)
        graduation_type = request.data.get('graduation_type', None)

        if bio is not None:
            if len(bio) > 256:
                return Response({"detail": "Your bio must be less than 256 characters. Shorten it up!"}, 405)
            elif bio == "Tell us a bit about yourself! What are you passionte about and what do you love to learn? This will be public.":
                bio = ""
            user.bio = bio

        if major is not None:
            if len(major) > 100:
                return Response({"detail": "Your major must be less than 100 characters. Abbreviate!"}, 405)
            user.major = major

        if class_year is not None:
            user.class_year = class_year

        if graduation_type is not None:
            user.graduation_type = graduation_type.upper()

        user.save()

        return Response(UserRegularInfoSerializer(user).data)

    @list_route(methods=['POST'])
    def resize_existing_pictures(self, request):
        path = 'images/profile_pictures'
        users = []

        for user in User.objects.all():
            if user.profile_picture:
                if get_file_from_s3(path, '%s_small.jpeg' % user.profile_picture):
                    # this user has sized images already
                    continue

                fp = get_file_from_s3(path, '%s.jpeg' % user.profile_picture)

                if not fp:
                    # there was an error retrieving their image, get rid of it
                    user.profile_picture = None
                    user.save()
                    continue

                size = 100, 100
                new_fp = get_resized_image(self, fp, size)
                file_name = '%s_small.jpeg' % user.profile_picture
                upload_image_to_s3(new_fp, path, file_name)

                size = 300, 300
                new_fp = get_resized_image(self, fp, size)
                file_name = '%s_medium.jpeg' % user.profile_picture
                upload_image_to_s3(new_fp, path, file_name)

                size = 600, 600
                new_fp = get_resized_image(self, fp, size)
                file_name = '%s_large.jpeg' % user.profile_picture
                upload_image_to_s3(new_fp, path, file_name)

                users.append(user.pk)

        return Response(users)

    @list_route(methods=['POST'], permission_classes=[IsAuthenticated])
    def upload_profile_picture(self, request):
        from django.utils.crypto import get_random_string

        path = 'images/profile_pictures'
        user = request.user

        current_photo = user.profile_picture
        if current_photo is not None:
            delete_image_from_s3(path, '%s_small.jpeg' % current_photo)
            delete_image_from_s3(path, '%s_medium.jpeg' % current_photo)
            delete_image_from_s3(path, '%s_large.jpeg' % current_photo)

        fp = request.FILES['profile_picture']
        base_name = get_random_string(20)
        user.profile_picture = base_name
        user.save()

        size = 100, 100
        new_fp = get_resized_image(self, fp, size)
        file_name = '%s_small.jpeg' % base_name
        upload_image_to_s3(new_fp, path, file_name)

        size = 300, 300
        new_fp = get_resized_image(self, fp, size)
        file_name = '%s_medium.jpeg' % base_name
        upload_image_to_s3(new_fp, path, file_name)

        size = 600, 600
        new_fp = get_resized_image(self, fp, size)
        file_name = '%s_large.jpeg' % base_name
        upload_image_to_s3(new_fp, path, file_name)

        return Response(UserRegularInfoSerializer(user).data)

    @list_route(methods=['GET'], permission_classes=[IsAuthenticated], url_path='get_husky_info')
    def get_husky_info(self, request):
        user = request.user

        # Check against pending tutors
        user.tutor.check_if_pending()
        user.refresh_from_db()
        user.tutor.refresh_from_db()

        serializer = UserHuskyInfoSerializer(user, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['GET'], permission_classes=[IsAuthenticated], url_path='get_full_info')
    def get_full_info(self, request):
        user = request.user

        # Check against pending tutors
        user.tutor.check_if_pending()
        user.refresh_from_db()
        user.tutor.refresh_from_db()

        serializer = UserFullInfoSerializer(user, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['POST'], url_path='login')
    def login(self, request):

        user = request.user

        if not request.auth:
            return Response({"status": "UNVERIFIED"})

        # See if the user has a tutor make one if not
        try:
            user.tutor
        except Tutor.DoesNotExist:
            user.tutor = Tutor.objects.create_default_tutor_with_user(user)

        # Same thing with student
        try:
            user.student
        except Student.DoesNotExist:
            user.student = Student.objects.create_default_student_with_user(user)

        user.save()

        # Check pending tutor stuff
        user.tutor.check_if_pending()
        user.refresh_from_db()
        user.tutor.refresh_from_db()
        if not user.profile_picture and not user.chavatar_color:
            user.assign_chavatar()

        serializer = UserFullInfoSerializer(user, context={'request': request})
        return Response({"status": "SUCCESS", "data": serializer.data, "session_id": request.auth.session_id})
