from rest_framework import serializers
from .models import *
from apps.tutor.serializers import TutorSerializer, TutorBasicSerializer
from apps.student.serializers import StudentSerializer, StudentBasicSerializer
from apps.university.serializers import SchoolSerializer, ConstantSerializer
from apps.transaction.models import OutstandingCharge
from apps.transaction.serializers import OutstandingChargeSerializer
from apps.group.serializers import ConversationSerializer
from apps.group.models import ConversationParticipant, Conversation
from apps.university.models import Constant
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


class UserSlimInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('full_name', 'profile_picture', 'major', 'id', 'chavatar_color')


class UserRegularInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('full_name', 'profile_picture', 'major', 'bio', 'class_year', 'graduation_type', 'id', 'chavatar_color')


class UserHuskyInfoSerializer(serializers.ModelSerializer):

    student = serializers.SerializerMethodField()
    tutor = serializers.SerializerMethodField()
    school = SchoolSerializer()
    sesh_state = SeshStateSerializer()
    cards = serializers.SerializerMethodField()
    outstanding_charges = serializers.SerializerMethodField()
    discounts = serializers.ReadOnlyField()
    constants = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ['password', 'salt']

    def get_constants(self, obj):
        try:
            constant = Constant.objects.get(school_id=obj.school.pk)
        except Constant.DoesNotExist:
            constant = Constant.objects.get(school_id=0)
        return ConstantSerializer(constant).data

    def get_student(self, obj):
        return StudentBasicSerializer(obj.student, context={'request': self.context['request']}).data

    def get_tutor(self, obj):
        return TutorBasicSerializer(obj.tutor, context={'request': self.context['request']}).data

    def get_cards(self, obj):
        return obj.get_cards()

    def get_outstanding_charges(self, obj):
        return OutstandingChargeSerializer(OutstandingCharge.objects.filter(user=obj), many=True).data


class UserFullInfoSerializer(serializers.ModelSerializer):

    student = serializers.SerializerMethodField()
    tutor = serializers.SerializerMethodField()
    school = SchoolSerializer()
    sesh_state = SeshStateSerializer()
    cards = serializers.SerializerMethodField()
    outstanding_charges = serializers.SerializerMethodField()
    discounts = serializers.ReadOnlyField()
    conversations = serializers.SerializerMethodField()
    constants = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ['password', 'salt']

    def get_constants(self, obj):
        try:
            constant = Constant.objects.get(school_id=obj.school.pk)
        except Constant.DoesNotExist:
            constant = Constant.objects.get(school_id=0)
        return ConstantSerializer(constant).data

    def get_conversations(self, obj):
        memberships = ConversationParticipant.objects.filter(user=obj)
        return ConversationSerializer(Conversation.objects.filter(id__in=memberships.values('conversation_id')), many=True, context={'request': self.context['request']}).data

    def get_student(self, obj):
        return StudentSerializer(obj.student, context={'request': self.context['request']}).data

    def get_tutor(self, obj):
        return TutorSerializer(obj.tutor, context={'request': self.context['request']}).data

    def get_cards(self, obj):
        return obj.get_cards()

    def get_outstanding_charges(self, obj):
        return OutstandingChargeSerializer(OutstandingCharge.objects.filter(user=obj), many=True).data
