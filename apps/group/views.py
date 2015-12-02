from .models import *
from rest_framework import viewsets
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from apps.university.models import Course
from apps.chatroom.models import Chatroom
from apps.account.serializers import UserBasicInfoSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions
import json


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer


class ConversationParticipantViewSet(viewsets.ModelViewSet):
    queryset = ConversationParticipant.objects.all()
    serializer_class = ConversationParticipantSerializer


class CourseGroupViewSet(viewsets.ModelViewSet):
    queryset = CourseGroup.objects.all()
    serializer_class = CourseGroupSerializer

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def create_study_group(self, request, pk=None):
        """
        Create a study_group
        """
        course_group = self.get_object()

        name = course_group.course.get_readable_name() + " Study Group"
        desc = "Study group for " + course_group.course.get_readable_name() + ", created by " + request.user.readable_name
        chatroom = Chatroom.objects.create(name=name, description=desc)
        chatroom.save()

        new_study_group = StudyGroup(user=request.user, chatroom=chatroom, course_group=course_group)
        new_study_group.save()

        obj = StudyGroupSerializer(new_study_group)
        return Response(obj.data)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def get_students(self, request, pk=None):
        """
        Get basic info for student members of a course_group
        """
        course_group = self.get_object()
        all_members = CourseGroupMember.objects.filter(course_group=course_group)
        all_users = [m.student.user for m in all_members]
        obj = UserBasicInfoSerializer(all_users, many=True)
        return Response(obj.data)

    @list_route(methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request):
        """
        Join a course_group
        """
        jsonArr = json.loads(request.POST.get('course_group_array'))
        user = request.user
        all_course_group_memberships = []

        for obj in jsonArr:

            course_group_id = obj.get('course_group_id', '')
            course_id = obj.get('course_id', '')
            professor_name = obj.get('professor_name', '')
            if not course_group_id:
                # must create a group to join
                try:
                    course = Course.objects.get(pk=course_id)
                except Course.DoesNotExist:
                    raise exceptions.NotFound("Course could not be found")
                chatroom = Chatroom.objects.create(name=course.get_readable_name(), description=course.name)
                chatroom.save()
                course_group = CourseGroup.objects.create(course=course, professor_name=professor_name, chatroom=chatroom)
                course_group.save()
            else:
                try:
                    course_group = CourseGroup.objects.get(pk=course_group_id)
                except CourseGroup.DoesNotExist:
                    raise exceptions.NotFound("Course Group could not be found")
                if (len(CourseGroupMember.objects.filter(course_group=course_group, student=user.student)) > 0):
                    continue

            # now add them to the group
            new_group_member = CourseGroupMember(course_group=course_group, student=user.student)
            new_group_member.save()
            all_course_group_memberships.append(new_group_member)

        serializer = CourseGroupMemberSerializer(all_course_group_memberships, many=True)
        return Response(serializer.data)


class CourseGroupMemberViewSet(viewsets.ModelViewSet):
    queryset = CourseGroupMember.objects.all()
    serializer_class = CourseGroupMemberSerializer


class StudyGroupViewSet(viewsets.ModelViewSet):
    queryset = StudyGroup.objects.all()
    serializer_class = StudyGroupSerializer
    permission_classes = [IsAuthenticated]

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        """
        Join a study_group
        """
        user = request.user
        study_group = self.get_object()

        if (len(StudyGroupMember.objects.filter(study_group=study_group, user=user)) > 0):
            return Response()

        new_group_member = StudyGroupMember(study_group=study_group, user=user)
        new_group_member.save()

        obj = StudyGroupMemberSerializer(new_group_member)
        return Response(obj.data)


class StudyGroupMemberViewSet(viewsets.ModelViewSet):
    queryset = StudyGroupMember.objects.all()
    serializer_class = StudyGroupMemberSerializer
