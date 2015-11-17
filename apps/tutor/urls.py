from django.conf.urls import include, url
from rest_framework import routers
from apps.tutor import views as tutor_views

router = routers.DefaultRouter()
router.register(r'open_tutor_promos', tutor_views.OpenTutorPromoViewSet);
router.register(r'past_tutor_promos', tutor_views.PastTutorPromoViewSet);
router.register(r'pending_tutor_classes', tutor_views.PendingTutorClassViewSet);
router.register(r'pending_tutors', tutor_views.PendingTutorViewSet);
router.register(r'tutor_classes', tutor_views.TutorClassViewSet);
router.register(r'tutor_departments', tutor_views.TutorDepartmentViewSet);
router.register(r'tutors', tutor_views.TutorViewSet);
router.register(r'tutor_signups', tutor_views.TutorSignupViewSet);
router.register(r'tutor_tiers', tutor_views.TutorTierViewSet);

urlpatterns = [
    url(r'^', include(router.urls))
]
