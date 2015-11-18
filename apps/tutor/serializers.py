from apps.tutor.models import OpenTutorPromo, PastTutorPromo, PendingTutorClass, PendingTutor, TutorClass, TutorDepartment, Tutor, TutorSignup, TutorTier
from rest_framework import serializers


class OpenTutorPromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenTutorPromo


class PastTutorPromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PastTutorPromo


class PendingTutorClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingTutorClass


class PendingTutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingTutor


class TutorClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorClass


class TutorDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorDepartment


class TutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutor


class TutorSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorSignup


class TutorTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorTier
