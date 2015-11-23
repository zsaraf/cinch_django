from apps.student.models import Favorite, Student
from rest_framework import viewsets
from apps.student.serializers import FavoriteSerializer, StudentSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
