from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
