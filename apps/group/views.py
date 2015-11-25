from .models import *
from rest_framework import viewsets
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from apps.university.models import Course
from apps.chatroom.models import Chatroom
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions


class CourseGroupViewSet(viewsets.ModelViewSet):
    queryset = CourseGroup.objects.all()
    serializer_class = CourseGroupSerializer

    @list_route(methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request):
        """
        Join a course_group
        """
        user = request.user
        course_group_id = request.POST.get('course_group_id', '')
        course_id = request.POST.get('course_id', '')
        professor_name = request.POST.get('professor_name', '')
        if not course_group_id:
            # must create a group to join
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist:
                raise exceptions.NotFound("Course could not be found")
            chatroom = Chatroom.objects.create(name=course.get_readable_name(), description=course.name)
            course_group = CourseGroup.objects.create(course=course, professor_name=professor_name, chatroom=chatroom)
            course_group.save()
            course_group_id=course_group.pk
        else:
            course_group = CourseGroup.objects.get(pk=course_group_id)

        # now add them to the group
        new_group_member = CourseGroupMember(course_group=course_group, student=user.student)
        new_group_member.save()
        
        obj = CourseGroupBasicSerializer(course_group)
        return Response(obj.data)


class CourseGroupMemberViewSet(viewsets.ModelViewSet):
    queryset = CourseGroupMember.objects.all()
    serializer_class = CourseGroupMemberSerializer


class StudyGroupViewSet(viewsets.ModelViewSet):
    queryset = StudyGroup.objects.all()
    serializer_class = StudyGroupSerializer


class StudyGroupMemberViewSet(viewsets.ModelViewSet):
    queryset = StudyGroupMember.objects.all()
    serializer_class = StudyGroupMemberSerializer
