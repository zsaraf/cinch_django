from apps.tutoring.models import OpenBid, SeshRequest, OpenSesh, PastBid, PastSesh, ReportedProblem
from apps.university.serializers import CourseSerializer
from rest_framework import serializers
import json
import logging
logger = logging.getLogger(__name__)


class OpenBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenBid


class NotificationSeshRequestSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    student_data = serializers.SerializerMethodField()
    estimated_wage = serializers.SerializerMethodField()

    class Meta:
        model = SeshRequest

    def get_student_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.student.user).data

    def get_estimated_wage(self, obj):
        return float(obj.get_estimated_wage())


class SeshRequestSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    tutor = serializers.SerializerMethodField()
    available_blocks = serializers.SerializerMethodField()
    student_data = serializers.SerializerMethodField()
    estimated_wage = serializers.SerializerMethodField()

    class Meta:
        model = SeshRequest

    def get_available_blocks(self, obj):
        if obj.available_blocks:
            return json.loads(obj.available_blocks)
        else:
            return None

    def get_estimated_wage(self, obj):
        return float(obj.get_estimated_wage())

    def get_student_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.student.user).data

    def get_tutor(self, obj):
        from apps.tutor.serializers import PeerTutorSerializer
        if obj.tutor is not None:
            return PeerTutorSerializer(obj.tutor).data
        else:
            return None


class SeshBasicRequestSerializer(SeshRequestSerializer):

    def get_tutor(self, obj):
        return None


class OpenSeshSerializer(serializers.ModelSerializer):
    past_request = SeshBasicRequestSerializer()
    chatroom = serializers.SerializerMethodField()
    user_data = serializers.SerializerMethodField()
    is_student = serializers.SerializerMethodField()

    class Meta:
        model = OpenSesh
        exclude = ('student', 'tutor', 'is_instant', 'has_received_set_start_time_initial_reminder', 'has_received_start_time_approaching_reminder')

    def get_chatroom(self, obj):
        from apps.chatroom.serializers import ChatroomSerializer
        return ChatroomSerializer(obj.chatroom, context={'request': self.context['request']}).data

    def get_user_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        request = self.context['request']
        if request.user == obj.tutor.user:
            return UserBasicInfoSerializer(obj.student.user).data
        else:
            return UserBasicInfoSerializer(obj.tutor.user).data

    def get_is_student(self, obj):
        request = self.context['request']
        if request.user == obj.student.user:
            return True
        else:
            return False


class PastBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = PastBid


class PastSeshSerializer(serializers.ModelSerializer):
    class Meta:
        model = PastSesh


class PastSeshStudentSerializer(serializers.ModelSerializer):
    tutor_data = serializers.SerializerMethodField()

    class Meta:
        model = PastSesh

    def get_tutor_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.tutor.user).data


class PastSeshTutorSerializer(serializers.ModelSerializer):
    student_data = serializers.SerializerMethodField()

    class Meta:
        model = PastSesh

    def get_student_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.student.user).data


class ReportedProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportedProblem
