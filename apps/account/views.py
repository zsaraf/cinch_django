from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.account.models import Device, DoNotEmail, EmailUserData, PasswordChangeRequest, PastBonus, PromoCode, SeshState, Token, User
from apps.account.serializers import (
    DeviceSerializer, DoNotEmailSerializer, EmailUserDataSerializer, PasswordChangeRequestSerializer,
    PastBonusSerializer, PromoCodeSerializer, SeshStateSerializer,  TokenSerializer, UserBasicInfoSerializer, UserFullInfoSerializer
)

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

    @list_route(methods=['GET'], permission_classes=[IsAuthenticated], url_path='get_full_info')
    def get_full_info(self, request):
        user = request.user

        # Check against pending tutors
        user.tutor.check_if_pending()
        user.refresh_from_db()
        user.tutor.refresh_from_db()

        serializer = UserFullInfoSerializer(user)
        return Response(serializer.data)
