from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import hashlib
import random
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
    serializer_class = UserBasicInfoSerializer

    def create(self, request):
        '''
        Create a new user
        '''
        from apps.university.models import School

        email = request.data.get('email').lower()
        full_name = request.data.get('full_name').title()
        password = request.data.get('password')
        promo_code = request.data.get('promo_code', None)
        pending_tutor_verification_id = request.data.get('pending_tutor_verification_id', None)
        version_number = float(request.data.get('version_number', 1.0))

        if version_number < 2:
            return Response("Download the latest version on the AppStore then try again!")

        try:
            existing_user = User.objects.get(email=email)
            if existing_user.is_verified:
                return Response("An account with that email already exists")
            else:
                str_to_hash = 'Eabltf1!' + existing_user.salt + password
                m = hashlib.sha1()
                m.update(str_to_hash)
                hex_dig = m.hexdigest()
                if existing_user.password == hex_dig:
                    return Response("Verify your account and log in!")
                else:
                    return Response("An account with that email already exists")

        except User.DoesNotExist:
            # brand new user

            # TODO validate entries

            length = 25
            chars = list(hashlib.md5(str(datetime.now())).digest())
            random.shuffle(chars)
            salt = str(chars[0: length])
            str_to_hash = 'Eabltf1!' + salt + password
            m = hashlib.sha1()
            m.update(str_to_hash)
            hex_dig = m.hexdigest()

            new_token = Token.objects.generate_new_token()
            is_verified = False

            # TODO if pending_tutor_verification_id is not None:
            #     # check for pending verification stuff and change is_verified if appropriate

            school = School.objects.get_school_from_email(email)

            state = SeshState.objects.get(identifier='SeshStateNone')
            user = User.objects.create(email=email, password=hex_dig, salt=salt, full_name=full_name, verification_id=new_token.session_id, school=school, sesh_state=state, is_verified=is_verified)

            return Response(UserBasicInfoSerializer(user).data)

    @list_route(methods=['POST'])
    def update_user_info(self, request):
        user = request.user
        bio = request.data.get('bio', None)
        major = request.data.get('major', None)
        class_year = request.data.get('class_year', None)
        graduation_type = request.data.get('graduation_type', None)

        if bio is not None:
            if len(bio) > 256:
                return Response("Your bio must be less than 256 characters. Shorten it up!")
            elif bio == "Tell us a bit about yourself! What are you passionte about and what do you love to learn? This will be public.":
                bio = ""
            user.bio = bio

        if major is not None:
            if len(major) > 100:
                return Response("Your major must be less than 100 characters. Abbreviate!")
            user.major = major

        if class_year is not None:
            user.class_year = class_year

        if graduation_type is not None:
            user.graduation_type = graduation_type.upper()

        user.save()

        return Response(UserBasicInfoSerializer(user).data)

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
            delete_image_from_s3(path, '%s.jpeg' % current_photo)
            delete_image_from_s3(path, '%s_small.jpeg' % current_photo)
            delete_image_from_s3(path, '%s_medium.jpeg' % current_photo)
            delete_image_from_s3(path, '%s_large.jpeg' % current_photo)

        fp = request.FILES['profile_picture']
        base_name = get_random_string(20)

        file_name = '%s.jpeg' % base_name
        upload_image_to_s3(fp, path, file_name)
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

        return Response(UserBasicInfoSerializer(user).data)

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
