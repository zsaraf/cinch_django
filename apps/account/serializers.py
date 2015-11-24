from rest_framework import serializers
from .models import *
from apps.tutor.serializers import TutorSerializer
from apps.student.serializers import StudentSerializer
from apps.university.serializers import SchoolSerializer
from apps.transaction.models import OutstandingCharge
from apps.transaction.serializers import OutstandingChargeSerializer


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device


class DoNotEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoNotEmail


class EmailUserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUserData


class PasswordChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordChangeRequest


class PastBonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PastBonus


class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode


class SeshStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeshState


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token


class UserBasicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('full_name', 'profile_picture', 'major', 'bio')


class UserFullInfoSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    tutor = TutorSerializer()
    school = SchoolSerializer()
    sesh_state = SeshStateSerializer()
    cards = serializers.SerializerMethodField()
    outstanding_charges = serializers.SerializerMethodField()
    discounts = serializers.ReadOnlyField()

    class Meta:
        model = User

    def get_cards(self, obj):
        return obj.get_cards()

    def get_outstanding_charges(self, obj):
        return OutstandingChargeSerializer(OutstandingCharge.objects.filter(user=obj), many=True).data
