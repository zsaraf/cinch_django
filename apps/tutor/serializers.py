from apps.tutor.models import OpenTutorPromo, PastTutorPromo, PendingTutorClass, PendingTutor, TutorCourse, TutorDepartment, Tutor, TutorSignup, TutorTier
from rest_framework import serializers
from apps.university.serializers import CourseSerializer, DepartmentSerializer
from apps.tutoring.serializers import PastSeshStudentSerializer, PastSeshTutorSerializer, OpenSeshSerializer
from apps.tutoring.models import OpenSesh
from django.conf import settings

import json
import os
import logging
logger = logging.getLogger(__name__)


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


class PeerTutorSerializer(serializers.ModelSerializer):
    tier = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Tutor

    def get_user(self, obj):
        from apps.account.serializers import UserRegularInfoSerializer
        return UserRegularInfoSerializer(obj.user).data

    def get_tier(self, obj):
        return TutorTierSerializer(obj.tier).data


class TutorBasicSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()
    departments = TutorDepartmentSerializer(many=True, source='tutordepartment_set')
    bonus_info = serializers.SerializerMethodField()
    tiers = serializers.SerializerMethodField()
    stats = serializers.ReadOnlyField()

    class Meta:
        model = Tutor

    def get_courses(self, obj):
        return TutorCourseSerializer(TutorCourse.objects.filter(tutor=obj), many=True).data

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


class TutorSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()
    departments = TutorDepartmentSerializer(many=True, source='tutordepartment_set')
    open_seshes = serializers.SerializerMethodField()
    past_seshes = PastSeshTutorSerializer(many=True, source='pastsesh_set')
    bonus_info = serializers.SerializerMethodField()
    tiers = serializers.SerializerMethodField()
    stats = serializers.ReadOnlyField()

    class Meta:
        model = Tutor

    def get_open_seshes(self, obj):
        return OpenSeshSerializer(OpenSesh.objects.filter(tutor=obj), many=True, context={'request': self.context['request']}).data

    def get_courses(self, obj):
        return TutorCourseSerializer(TutorCourse.objects.filter(tutor=obj), many=True).data

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
