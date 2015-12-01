from rest_framework import serializers
from .models import *
from apps.university.serializers import CourseSerializer
from apps.chatroom.serializers import ChatroomSerializer

class CourseGroupBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseGroup

class CourseGroupSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    chatroom = ChatroomSerializer()

    class Meta:
        model = CourseGroup


class CourseGroupMemberSerializer(serializers.ModelSerializer):
    course_group = CourseGroupSerializer()

    class Meta:
        model = CourseGroupMember
        fields = (['course_group'])


class StudyGroupSerializer(serializers.ModelSerializer):
    # chatroom = ChatroomSerializer
    # creator = UserBasicInfoSerializer

    class Meta:
        model = StudyGroup
        # fields = (['chatroom', 'creator'])


class StudyGroupMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudyGroupMember
