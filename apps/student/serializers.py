from rest_framework import serializers
from .models import *
from apps.group.serializers import CourseGroupMemberSerializer
from apps.tutoring.serializers import OpenSeshStudentSerializer, PastSeshStudentSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    user_data = serializers.SerializerMethodField()

    class Meta:
        model = Favorite

    def get_user_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.tutor.user).data


class StudentSerializer(serializers.ModelSerializer):
    favorite_set = FavoriteSerializer(many=True)
    open_seshes = OpenSeshStudentSerializer(many=True, source='opensesh_set')
    past_seshes = PastSeshStudentSerializer(many=True, source='pastsesh_set')
    courses = CourseGroupMemberSerializer(many=True, source='coursegroupmember_set')
    stats = serializers.ReadOnlyField()

    class Meta:
        model = Student
