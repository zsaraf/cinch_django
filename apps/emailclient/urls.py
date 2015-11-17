from django.conf.urls import include, url
from rest_framework import routers
from apps.emailclient import views

router = routers.DefaultRouter()
router.register(r'pending_emails', views.PendingEmailViewSet);

urlpatterns = [
    url(r'^', include(router.urls))
]
