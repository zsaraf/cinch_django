from django.conf.urls import include, url
from rest_framework import routers
from apps.group import views as group_views

router = routers.DefaultRouter()
router.register(r'course_groups', group_views.CourseGroupViewSet)
router.register(r'study_groups', group_views.StudyGroupViewSet)
router.register(r'conversations', group_views.ConversationViewSet)


urlpatterns = [
    url(r'^', include(router.urls))
]
