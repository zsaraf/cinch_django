from rest_framework import viewsets
from api.models import User
from api.models import Student
from api.serializers import UserSerializer
from api.serializers import StudentSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer

class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Student.objects.all().order_by('-id')
    serializer_class = StudentSerializer

