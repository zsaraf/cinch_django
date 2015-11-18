from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.account.models import Device, DoNotEmail, EmailUserData, PasswordChangeRequest, PastBonus, PromoCode, SeshState, Token, User
from apps.account.serializers import DeviceSerializer, DoNotEmailSerializer, EmailUserDataSerializer, PasswordChangeRequestSerializer, \
                                     PastBonusSerializer, PromoCodeSerializer, SeshStateSerializer,  TokenSerializer, UserSerializer
from apps.student.serializers import StudentSerializer
from apps.tutor.serializers import TutorSerializer
from apps.university.serializers import SchoolSerializer
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
    serializer_class = UserSerializer

    @detail_route(methods=['get'],
                  permission_classes=[IsAuthenticated],
                  url_path='get_full_info')
    def get_full_info(self, request, pk=None):
        user = self.get_object()

        responseObject = {}
        responseObject['session_id'] = user.token.session_id
        responseObject['student'] = StudentSerializer(user.student).data
        responseObject['tutor'] = TutorSerializer(user.tutor).data
        responseObject['school'] = SchoolSerializer(user.school).data
        return Response(responseObject)
