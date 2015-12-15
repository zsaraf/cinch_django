from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from sesh.s3utils import upload_png_to_s3
from .models import *
from .serializers import *
from .AuthenticationBackend import SeshAuthentication
from apps.tutor.models import Tutor
from apps.student.models import Student
import json
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

    @list_route(methods=['POST'], permission_classes=[IsAuthenticated], url_path='upload_profile_picture')
    def upload_profile_picture(self, request):
        from PIL import Image
        from StringIO import StringIO
        from django.utils.crypto import get_random_string

        user = request.user
        fp = request.FILES['profile_picture']
        base_name = get_random_string(20)
        path = 'images/profile_pictures'

        file_name = '%s.png' % base_name
        url = upload_png_to_s3(fp, path, file_name)
        user.profile_picture = url
        user.save()

        fp.seek(0)
        size = 100, 100
        image = Image.open(fp)
        image.thumbnail(size, Image.ANTIALIAS)
        small_fp = StringIO()
        image.save(small_fp, 'png')
        file_name = '%s_small.png' % base_name
        small_fp.seek(0)
        upload_png_to_s3(small_fp, path, file_name)

        fp.seek(0)
        size = 300, 300
        image = Image.open(fp)
        image.thumbnail(size, Image.ANTIALIAS)
        med_fp = StringIO()
        image.save(med_fp, 'png')
        file_name = '%s_medium.png' % base_name
        med_fp.seek(0)
        upload_png_to_s3(med_fp, path, file_name)

        fp.seek(0)
        size = 600, 600
        image = Image.open(fp)
        image.thumbnail(size, Image.ANTIALIAS)
        large_fp = StringIO()
        image.save(large_fp, 'png')
        file_name = '%s_large.png' % base_name
        large_fp.seek(0)
        upload_png_to_s3(large_fp, path, file_name)

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
