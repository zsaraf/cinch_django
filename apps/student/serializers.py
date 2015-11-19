from apps.student.models import Student, Favorite, StudentCourse
from rest_framework import serializers


class FavoriteSerializer(serializers.ModelSerializer):
    user_data = serializers.SerializerMethodField()

    class Meta:
        model = Favorite

    def get_user_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.tutor.user)


class StudentSerializer(serializers.ModelSerializer):
    favorite_set = FavoriteSerializer(many=True)

    class Meta:
        model = Student


class StudentCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCourse
