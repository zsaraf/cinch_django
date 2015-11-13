from rest_framework import serializers
from api.models import User
from api.models import Student

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')

class StudentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Student
