from apps.tutor.models import OpenTutorPromo, PastTutorPromo, PendingTutorClass, PendingTutor, TutorClass, TutorDepartment, Tutor, TutorSignup, TutorTier
from rest_framework import serializers

class OpenTutorPromoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpenTutorPromo

class PastTutorPromoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PastTutorPromo

class PendingTutorClassSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PendingTutorClass
        
class PendingTutorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PendingTutor

class TutorClassSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TutorClass

class TutorDepartmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TutorDepartment

class TutorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tutor

class TutorSignupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TutorSignup

class TutorTierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TutorTier