from apps.tutor.models import OpenTutorPromo, PastTutorPromo, PendingTutorClass, PendingTutor, TutorCourse, TutorDepartment, Tutor, TutorSignup, TutorTier
from rest_framework import serializers
from apps.university.serializers import CourseSerializer, DepartmentSerializer
from django.conf import settings

import json
import os


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


class TutorCourseSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = TutorCourse


class TutorDepartmentSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()

    class Meta:
        model = TutorDepartment


class TutorTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorTier


class TutorSerializer(serializers.ModelSerializer):
    courses = TutorCourseSerializer(many=True, source='tutorcourse_set')
    departments = TutorDepartmentSerializer(many=True, source='tutordepartment_set')
    bonus_info = serializers.SerializerMethodField()
    tiers = serializers.SerializerMethodField()
    stats = serializers.ReadOnlyField()

    class Meta:
        model = Tutor

    def get_bonus_info(self, obj):
        with open(os.path.join(settings.ROOT_DIR, 'files/monthly_bonus.json'), 'r') as f:
            monthly_bonus_description = json.load(f)
            school = obj.user.school

            if str(school.id) in monthly_bonus_description:
                return monthly_bonus_description[str(school.id)]
            else:
                return monthly_bonus_description["0"]

    def get_tiers(self, obj):
        return TutorTierSerializer(TutorTier.objects.all(), many=True).data


class TutorSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorSignup
