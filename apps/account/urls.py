from django.conf.urls import include, url
from rest_framework import routers
from apps.account import views

router = routers.DefaultRouter()
router.register(r'devices', views.DeviceViewSet)
router.register(r'do_not_emails', views.DoNotEmailViewSet)
router.register(r'email_user_data', views.EmailUserDataViewSet)
router.register(r'password_change_requests',
                views.PasswordChangeRequestViewSet)
router.register(r'past_bonuses', views.PastBonusViewSet)
router.register(r'promo_codes', views.PromoCodeViewSet)
router.register(r'sesh_states', views.SeshStateViewSet)
router.register(r'tokens', views.TokenViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
