from apps.tutoring.models import OpenBid, OpenRequest, Request, OpenSesh, PastBid, PastRequest, PastSesh, ReportedProblem
from apps.university.serializers import CourseSerializer
from apps.chatroom.serializers import ChatroomSerializer
from rest_framework import serializers
import json


class OpenBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenBid


class OpenRequestSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    available_blocks = serializers.SerializerMethodField()

    class Meta:
        model = OpenRequest

    def get_available_blocks(self, obj):
        return json.loads(obj.available_blocks)


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request


class OpenRequestStudentSerializer(OpenRequestSerializer):
    class Meta:
        model = OpenRequest


class PastRequestSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = PastRequest


class OpenSeshSerializer(serializers.ModelSerializer):
    past_request = RequestSerializer()
    chatroom = ChatroomSerializer()

    class Meta:
        model = OpenSesh


class OpenSeshStudentSerializer(OpenSeshSerializer):
    tutor_data = serializers.SerializerMethodField()

    class Meta:
        model = OpenSesh

    def get_tutor_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.tutor.user).data


class OpenSeshTutorSerializer(OpenSeshSerializer):
    student_data = serializers.SerializerMethodField()

    class Meta:
        model = OpenSesh

    def get_student_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.student.user).data


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
