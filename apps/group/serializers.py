from rest_framework import serializers
from .models import *
from apps.university.serializers import CourseSerializer
from apps.chatroom.serializers import ChatroomSerializer


class ConversationSerializer(serializers.ModelSerializer):
    chatroom = ChatroomSerializer()

    class Meta:
        model = Conversation


class ConversationParticipantSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer()

    class Meta:
        model = ConversationParticipant


class CourseGroupBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseGroup


class StudyGroupSerializer(serializers.ModelSerializer):
    chatroom = ChatroomSerializer()

    class Meta:
        model = StudyGroup


class CourseGroupSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    chatroom = ChatroomSerializer()
    study_groups = StudyGroupSerializer(many=True, source="studygroup_set")
    tutors = serializers.SerializerMethodField()

    class Meta:
        model = CourseGroup

    def get_tutors(self, obj):
        from apps.tutor.models import Tutor, TutorCourse
        from apps.tutor.serializers import TutorSerializer
        courses = TutorCourse.objects.filter(course=obj.course)
        return TutorSerializer(Tutor.objects.filter(id__in=courses.values('tutor_id')), many=True).data


class CourseGroupMemberSerializer(serializers.ModelSerializer):
    course_group = CourseGroupSerializer()

    class Meta:
        model = CourseGroupMember
        fields = (['course_group'])


class StudyGroupMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudyGroupMember
