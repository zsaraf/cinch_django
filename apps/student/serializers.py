from rest_framework import serializers
from .models import *
from apps.tutoring.serializers import OpenSeshStudentSerializer, PastSeshStudentSerializer, OpenSeshRequestStudentSerializer


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
    from apps.group.serializers import CourseGroupMemberSerializer
    favorite_set = FavoriteSerializer(many=True)
    open_seshes = OpenSeshStudentSerializer(many=True, source='opensesh_set')
    past_seshes = PastSeshStudentSerializer(many=True, source='pastsesh_set')
    open_requests = serializers.SerializerMethodField()
    courses = CourseGroupMemberSerializer(many=True, source='coursegroupmember_set')
    stats = serializers.ReadOnlyField()

    class Meta:
        model = Student

    def get_open_requests(self, obj):
        from apps.tutoring.models import SeshRequest
        return OpenSeshRequestStudentSerializer(SeshRequest.objects.filter(student=obj, status=0), many=True).data
