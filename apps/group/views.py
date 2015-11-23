from .models import *
from rest_framework import viewsets
from .serializers import *


class CourseGroupViewSet(viewsets.ModelViewSet):
    queryset = CourseGroup.objects.all()
    serializer_class = CourseGroupSerializer


class CourseGroupMemberViewSet(viewsets.ModelViewSet):
    queryset = CourseGroupMember.objects.all()
    serializer_class = CourseGroupMemberSerializer


class StudyGroupViewSet(viewsets.ModelViewSet):
    queryset = StudyGroup.objects.all()
    serializer_class = StudyGroupSerializer


class StudyGroupMemberViewSet(viewsets.ModelViewSet):
    queryset = StudyGroupMember.objects.all()
    serializer_class = StudyGroupMemberSerializer
