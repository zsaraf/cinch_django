from apps.student.models import Student, Favorite
from rest_framework import serializers

class FavoriteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Favorite
            
class StudentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Student
