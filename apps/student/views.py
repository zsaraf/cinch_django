from apps.student.models import Favorite, Student, StudentCourse
from rest_framework import viewsets
from apps.student.serializers import FavoriteSerializer, StudentSerializer, StudentCourseSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentCourseViewSet(viewsets.ModelViewSet):
    queryset = StudentCourse.objects.all()
    serializer_class = StudentCourseSerializer
