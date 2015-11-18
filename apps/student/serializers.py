from apps.student.models import Student, Favorite, StudentCourse
from rest_framework import serializers


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student


class StudentCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCourse
