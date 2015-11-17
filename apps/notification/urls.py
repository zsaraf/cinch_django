from django.conf.urls import include, url
from rest_framework import routers
from apps.notification import views

router = routers.DefaultRouter()
router.register(r'notification_types', views.NotificationTypeViewSet);
router.register(r'open_notifications', views.OpenNotificationViewSet);
router.register(r'past_notifications', views.PastNotificationViewSet);

urlpatterns = [
    url(r'^', include(router.urls))
]
