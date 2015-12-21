from rest_framework import serializers
from .models import *
from apps.tutoring.serializers import OpenSeshTutorSerializer, PastSeshStudentSerializer, OpenSeshRequestStudentSerializer
from apps.group.serializers import CourseGroupSerializer
from apps.group.models import CourseGroup, CourseGroupMember
from apps.tutoring.models import OpenSesh


class FavoriteSerializer(serializers.ModelSerializer):
    user_data = serializers.SerializerMethodField()

    class Meta:
        model = Favorite

    def get_user_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.tutor.user).data


class StudentUserInfoSerializer(serializers.ModelSerializer):
    user_data = serializers.SerializerMethodField()

    class Meta:
        model = Student

    def get_user_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.user).data


class StudentSerializer(serializers.ModelSerializer):
    favorites = serializers.SerializerMethodField()
    open_seshes = serializers.SerializerMethodField()
    past_seshes = PastSeshStudentSerializer(many=True, source='pastsesh_set')
    open_requests = serializers.SerializerMethodField()
    course_groups = serializers.SerializerMethodField()
    stats = serializers.ReadOnlyField()

    class Meta:
        model = Student

    def get_favorites(self, obj):
        return FavoriteSerializer(source='favorite_set', many=True).data

    def get_open_seshes(self, obj):
        return OpenSeshTutorSerializer(source='opensesh_set', many=True, context={'request': self.context['request']}).data

    def get_course_groups(self, obj):
        course_group_memberships = CourseGroupMember.objects.filter(student=obj, is_past=False)
        return CourseGroupSerializer(CourseGroup.objects.filter(id__in=course_group_memberships.values('course_group_id')), many=True, context={'request': self.context['request']}).data

    def get_open_requests(self, obj):
        from apps.tutoring.models import SeshRequest
        return OpenSeshRequestStudentSerializer(SeshRequest.objects.filter(student=obj, status=0), many=True).data
