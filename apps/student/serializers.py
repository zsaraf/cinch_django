from rest_framework import serializers
from .models import *
from apps.tutoring.serializers import OpenSeshSerializer, PastSeshStudentSerializer, SeshRequestSerializer
from apps.tutoring.models import OpenSesh
from apps.group.serializers import CourseGroupFullSerializer
from apps.group.models import CourseGroup, CourseGroupMember
import logging
logger = logging.getLogger(__name__)


class FavoriteSerializer(serializers.ModelSerializer):
    user_data = serializers.SerializerMethodField()
    tutor_id = serializers.SerializerMethodField()
    tier = serializers.SerializerMethodField()

    class Meta:
        model = Favorite

    def get_tutor_id(self, obj):
        return obj.tutor.pk

    def get_user_data(self, obj):
        from apps.account.serializers import UserRegularInfoSerializer
        return UserRegularInfoSerializer(obj.tutor.user).data

    def get_tier(self, obj):
        from apps.tutor.serializers import TutorTierSerializer
        return TutorTierSerializer(obj.tutor.tier).data


class StudentUserInfoSerializer(serializers.ModelSerializer):
    user_data = serializers.SerializerMethodField()

    class Meta:
        model = Student

    def get_user_data(self, obj):
        from apps.account.serializers import UserRegularInfoSerializer
        return UserRegularInfoSerializer(obj.user).data


class StudentBasicSerializer(serializers.ModelSerializer):
    favorites = serializers.SerializerMethodField()
    requests = serializers.SerializerMethodField()
    stats = serializers.ReadOnlyField()

    class Meta:
        model = Student

    def get_favorites(self, obj):
        return FavoriteSerializer(Favorite.objects.filter(student=obj), many=True).data

    def get_requests(self, obj):
        from apps.tutoring.models import SeshRequest
        return SeshRequestSerializer(SeshRequest.objects.filter(student=obj, status=0), many=True).data


class StudentSerializer(StudentBasicSerializer):
    open_seshes = serializers.SerializerMethodField()
    past_seshes = PastSeshStudentSerializer(many=True, source='pastsesh_set')
    course_groups = serializers.SerializerMethodField()

    class Meta:
        model = Student

    def get_open_seshes(self, obj):
        return OpenSeshSerializer(OpenSesh.objects.filter(student=obj), many=True, context={'request': self.context['request']}).data

    def get_course_groups(self, obj):
        course_group_memberships = CourseGroupMember.objects.filter(student=obj, is_past=False)
        return CourseGroupFullSerializer(CourseGroup.objects.filter(is_past=False, id__in=course_group_memberships.values('course_group_id')), many=True, context={'request': self.context['request']}).data
