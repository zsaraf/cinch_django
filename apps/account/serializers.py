from rest_framework import serializers
from .models import *
from apps.tutor.serializers import TutorSerializer
from apps.student.serializers import StudentSerializer
from apps.university.serializers import SchoolSerializer
from apps.transaction.models import OutstandingCharge
from apps.transaction.serializers import OutstandingChargeSerializer
from apps.group.serializers import ConversationParticipantSerializer
import logging
logger = logging.getLogger(__name__)


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
        fields = ('full_name', 'profile_picture', 'major', 'bio', 'id', 'chavatar_color')


class UserFullInfoSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    tutor = serializers.SerializerMethodField()
    school = SchoolSerializer()
    sesh_state = SeshStateSerializer()
    cards = serializers.SerializerMethodField()
    outstanding_charges = serializers.SerializerMethodField()
    discounts = serializers.ReadOnlyField()
    conversations = ConversationParticipantSerializer(many=True, source='conversationparticipant_set')

    class Meta:
        model = User

    def get_student(self, obj):
        return StudentSerializer(obj.student, context={'request': self.context['request']}).data

    def get_tutor(self, obj):
        return TutorSerializer(obj.tutor, context={'request': self.context['request']}).data

    def get_cards(self, obj):
        return obj.get_cards()

    def get_outstanding_charges(self, obj):
        return OutstandingChargeSerializer(OutstandingCharge.objects.filter(user=obj), many=True).data
