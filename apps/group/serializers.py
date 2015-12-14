from rest_framework import serializers
from .models import *
from apps.university.serializers import CourseSerializer
from apps.chatroom.serializers import ChatroomSerializer


class ConversationParticipantSerializer(serializers.ModelSerializer):
    # conversation = ConversationSerializer()

    class Meta:
        model = ConversationParticipant
        

class ConversationSerializer(serializers.ModelSerializer):
    chatroom = ChatroomSerializer()
    conversation_participants = ConversationParticipantSerializer(many=True, source="conversationparticipant_set")

    class Meta:
        model = Conversation


class CourseGroupBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseGroup


class StudyGroupSerializer(serializers.ModelSerializer):
    chatroom = ChatroomSerializer()

    class Meta:
        model = StudyGroup


class CourseGroupMemberSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = CourseGroupMember

    def get_user(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.student.user).data


class CourseGroupSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    chatroom = ChatroomSerializer()
    study_groups = StudyGroupSerializer(many=True, source="studygroup_set")
    tutors = serializers.SerializerMethodField()
    members = CourseGroupMemberSerializer(many=True, source="coursegroupmember_set")

    class Meta:
        model = CourseGroup

    def get_tutors(self, obj):
        from apps.tutor.models import Tutor, TutorCourse
        from apps.tutor.serializers import TutorCourseGroupSerializer
        courses = TutorCourse.objects.filter(course=obj.course)
        return TutorCourseGroupSerializer(Tutor.objects.filter(id__in=courses.values('tutor_id')), many=True).data


class StudyGroupMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudyGroupMember
