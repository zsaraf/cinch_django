from django.conf.urls import include, url
from rest_framework import routers
from apps.student import views

router = routers.DefaultRouter()
router.register(r'open_tutor_promos', views.FavoriteViewSet);
router.register(r'past_tutor_promos', views.StudentViewSet);

urlpatterns = [
    url(r'^', include(router.urls))
]
