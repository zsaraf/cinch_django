from rest_framework import serializers
from .models import *
from apps.university.serializers import CourseSerializer
from apps.chatroom.serializers import ChatroomSerializer
import logging
logger = logging.getLogger(__name__)


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


class StudyGroupMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudyGroupMember


class StudyGroupSerializer(serializers.ModelSerializer):
    chatroom = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = StudyGroup

    def get_members(self, obj):
        return StudyGroupMemberSerializer(StudyGroupMember.objects.filter(study_group=obj, is_past=False), many=True).data

    def get_chatroom(self, obj):
        return ChatroomSerializer(obj.chatroom, context={'request': self.context['request']}).data


class CourseGroupMemberSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = CourseGroupMember

    def get_user(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.student.user).data


class CourseGroupSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    chatroom = serializers.SerializerMethodField()
    study_groups = serializers.SerializerMethodField()
    tutors = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = CourseGroup

    def get_members(self, obj):
        return CourseGroupMemberSerializer(CourseGroupMember.objects.filter(course_group=obj, is_past=False), many=True).data

    def get_chatroom(self, obj):
        return ChatroomSerializer(obj.chatroom, context={'request': self.context['request']}).data

    def get_study_groups(self, obj):
        return StudyGroupSerializer(many=True, source="studygroup_set", context={'request': self.context['request']}).data

    def get_tutors(self, obj):
        from apps.tutor.models import Tutor, TutorCourse
        from apps.tutor.serializers import TutorCourseGroupSerializer
        from apps.tutoring.models import PastSesh

        seshes = PastSesh.objects.filter(past_request__course=obj.course)
        tutors = [item.tutor.id for item in seshes]
        courses = TutorCourse.objects.filter(course=obj.course)
        tutors.extend([item.tutor.id for item in courses])

        return TutorCourseGroupSerializer(Tutor.objects.filter(id__in=tutors), many=True).data


