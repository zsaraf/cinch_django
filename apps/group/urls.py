from django.conf.urls import include, url
from rest_framework import routers
from apps.group import views as group_views

router = routers.DefaultRouter()
router.register(r'course_groups', group_views.CourseGroupViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]