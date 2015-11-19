from apps.tutor.models import OpenTutorPromo, PastTutorPromo, PendingTutorClass, PendingTutor, TutorCourse, TutorDepartment, Tutor, TutorSignup, TutorTier
from rest_framework import viewsets
from apps.tutor.serializers import OpenTutorPromoSerializer, PastTutorPromoSerializer, PendingTutorClassSerializer, PendingTutorSerializer, \
                                   TutorCourseSerializer, TutorDepartmentSerializer, TutorSerializer, TutorSignupSerializer, TutorTierSerializer


class OpenTutorPromoViewSet(viewsets.ModelViewSet):
    queryset = OpenTutorPromo.objects.all()
    serializer_class = OpenTutorPromoSerializer


class PastTutorPromoViewSet(viewsets.ModelViewSet):
    queryset = PastTutorPromo.objects.all()
    serializer_class = PastTutorPromoSerializer


class PendingTutorClassViewSet(viewsets.ModelViewSet):
    queryset = PendingTutorClass.objects.all()
    serializer_class = PendingTutorClassSerializer


class PendingTutorViewSet(viewsets.ModelViewSet):
    queryset = PendingTutor.objects.all()
    serializer_class = PendingTutorSerializer


class TutorCourseViewSet(viewsets.ModelViewSet):
    queryset = TutorCourse.objects.all()
    serializer_class = TutorCourseSerializer


class TutorDepartmentViewSet(viewsets.ModelViewSet):
    queryset = TutorDepartment.objects.all()
    serializer_class = TutorDepartmentSerializer


class TutorViewSet(viewsets.ModelViewSet):
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer


class TutorSignupViewSet(viewsets.ModelViewSet):
    queryset = TutorSignup.objects.all()
    serializer_class = TutorSignupSerializer


class TutorTierViewSet(viewsets.ModelViewSet):
    queryset = TutorTier.objects.all()
    serializer_class = TutorTierSerializer
