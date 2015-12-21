from apps.tutoring.models import OpenBid, SeshRequest, OpenSesh, PastBid, PastSesh, ReportedProblem
from apps.university.serializers import CourseSerializer
from rest_framework import serializers


class OpenBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenBid


class SeshRequestSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    tutor = serializers.SerializerMethodField()

    class Meta:
        model = SeshRequest

    def get_tutor(self, obj):
        from apps.tutor.serializers import PeerTutorSerializer
        return PeerTutorSerializer(obj.tutor).data


class OpenSeshRequestStudentSerializer(SeshRequestSerializer):
    class Meta:
        model = SeshRequest


class OpenSeshSerializer(serializers.ModelSerializer):
    past_request = SeshRequestSerializer()
    chatroom = serializers.SerializerMethodField()

    class Meta:
        model = OpenSesh

    def get_chatroom(self, obj):
        from apps.chatroom.serializers import ChatroomSerializer
        return ChatroomSerializer(obj.chatroom, context={'request': self.context['request']}).data


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
