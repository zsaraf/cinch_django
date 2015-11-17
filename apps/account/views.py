from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from apps.account.models import Device, DoNotEmail, EmailUserData, PasswordChangeRequest, PastBonus, PromoCode, SeshState, Token, User
from apps.account.serializers import DeviceSerializer, DoNotEmailSerializer, EmailUserDataSerializer, PasswordChangeRequestSerializer, PastBonusSerializer, PromoCodeSerializer, SeshStateSerializer, TokenSerializer, UserSerializer

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