from apps.group.models import *
from apps.university.serializers import CourseSerializer
from rest_framework import serializers


class CourseGroupSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = CourseGroup


class CourseGroupMemberSerializer(serializers.ModelSerializer):
    course_group = CourseGroupSerializer()

    class Meta:
        model = CourseGroupMember
        fields = ('course_group', )


class StudyGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudyGroup


class StudyGroupMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudyGroupMember
