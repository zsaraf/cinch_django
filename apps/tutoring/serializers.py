from apps.tutoring.models import OpenBid, OpenRequest, OpenSesh, PastBid, PastRequest, PastSesh, ReportedProblem
from apps.university.serializers import CourseSerializer
from rest_framework import serializers


class OpenBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenBid


class OpenRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenRequest


class PastRequestSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = PastRequest


class OpenSeshSerializer(serializers.ModelSerializer):
    pastrequest = PastRequestSerializer()

    class Meta:
        model = OpenSesh


class OpenSeshStudentSerializer(OpenSeshSerializer):
    tutor_data = serializers.SerializerMethodField()

    class Meta:
        model = OpenSesh

    def get_tutor_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.tutor.user)


class OpenSeshTutorSerializer(OpenSeshSerializer):
    student_data = serializers.SerializerMethodField()

    class Meta:
        model = OpenSesh

    def get_student_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.student.user)


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
        return UserBasicInfoSerializer(obj.tutor.user)


class PastSeshTutorSerializer(serializers.ModelSerializer):
    student_data = serializers.SerializerMethodField()

    class Meta:
        model = PastSesh

    def get_student_data(self, obj):
        from apps.account.serializers import UserBasicInfoSerializer
        return UserBasicInfoSerializer(obj.student.user)


class ReportedProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportedProblem
