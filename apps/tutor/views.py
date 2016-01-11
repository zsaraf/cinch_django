from .models import *
from .serializers import *
from apps.student.models import Favorite
from apps.student.serializers import FavoriteSerializer
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


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
    permission_classes = [IsAuthenticated]

    @detail_route(methods=['post'])
    def toggle_favorite(self, request, pk=None):

        tutor = self.get_object()

        # Check if favorite already exists
        favorites = Favorite.objects.filter(student=request.user.student, tutor=tutor)
        if favorites.count() > 0:
            # Remove the favorite
            favorites.delete()
            return Response()
        else:
            # Add the favorite
            return Response(FavoriteSerializer(Favorite.objects.create(student=request.user.student, tutor=tutor)).data)


class TutorSignupViewSet(viewsets.ModelViewSet):
    queryset = TutorSignup.objects.all()
    serializer_class = TutorSignupSerializer


class TutorTierViewSet(viewsets.ModelViewSet):
    queryset = TutorTier.objects.all()
    serializer_class = TutorTierSerializer
