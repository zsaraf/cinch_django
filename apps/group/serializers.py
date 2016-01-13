from rest_framework import serializers
from .models import *
from apps.university.serializers import CourseSerializer
from apps.chatroom.serializers import ChatroomSerializer
import logging
logger = logging.getLogger(__name__)


class ConversationParticipantSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConversationParticipant


class ConversationSerializer(serializers.ModelSerializer):
    chatroom = serializers.SerializerMethodField()

    class Meta:
        model = Conversation

    def get_chatroom(self, obj):
        return ChatroomSerializer(obj.chatroom, context={'request': self.context['request']}).data


class CourseGroupSlimSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseGroup


class StudyGroupMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudyGroupMember


class StudyGroupBasicSerializer(serializers.ModelSerializer):
    # TODO For activity PN need to have chatroom_member? think about this when study groups implemented

    class Meta:
        model = StudyGroup


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
        from apps.account.serializers import UserRegularInfoSerializer
        return UserRegularInfoSerializer(obj.student.user).data


class CourseGroupRegularSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    tutors = serializers.SerializerMethodField()
    course = CourseSerializer()

    class Meta:
        model = CourseGroup

    def get_members(self, obj):
        return CourseGroupMemberSerializer(CourseGroupMember.objects.filter(course_group=obj, is_past=False), many=True).data

    def get_tutors(self, obj):
        from apps.tutor.models import Tutor, TutorCourse
        from apps.tutor.serializers import PeerTutorSerializer
        from apps.tutoring.models import PastSesh

        seshes = PastSesh.objects.filter(past_request__course=obj.course)
        tutors = [item.tutor.id for item in seshes]
        courses = TutorCourse.objects.filter(course=obj.course)
        tutors.extend([item.tutor.id for item in courses])

        return PeerTutorSerializer(Tutor.objects.filter(id__in=tutors), many=True).data


class CourseGroupFullSerializer(serializers.ModelSerializer):
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
        open_groups = StudyGroup.objects.filter(course_group=obj, is_past=False)
        return StudyGroupBasicSerializer(open_groups, many=True, context={'request': self.context['request']}).data

    def get_tutors(self, obj):
        from apps.tutor.models import Tutor, TutorCourse
        from apps.tutor.serializers import PeerTutorSerializer
        from apps.tutoring.models import PastSesh

        seshes = PastSesh.objects.filter(past_request__course=obj.course)
        tutors = [item.tutor.id for item in seshes]
        courses = TutorCourse.objects.filter(course=obj.course)
        tutors.extend([item.tutor.id for item in courses])

        return PeerTutorSerializer(Tutor.objects.filter(id__in=tutors), many=True).data
