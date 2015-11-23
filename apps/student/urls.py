from django.conf.urls import include, url
from rest_framework import routers
from apps.student import views

router = routers.DefaultRouter()
router.register(r'favorites', views.FavoriteViewSet)
router.register(r'students', views.StudentViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
