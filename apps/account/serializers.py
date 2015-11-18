from apps.account.models import Device, DoNotEmail, EmailUserData, PasswordChangeRequest, PastBonus, PromoCode, SeshState, Token, User
from rest_framework import serializers


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Device


class DoNotEmailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DoNotEmail


class EmailUserDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmailUserData


class PasswordChangeRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PasswordChangeRequest


class PastBonusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PastBonus


class PromoCodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PromoCode


class SeshStateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SeshState


class TokenSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Token


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
