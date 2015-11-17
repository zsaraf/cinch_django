from django.conf.urls import include, url
from rest_framework import routers
from apps.university import views

router = routers.DefaultRouter()
router.register(r'bonus_point_allocations', views.BonusPointAllocationViewSet);
router.register(r'classes', views.ClassViewSet)
router.register(r'constants', views.ConstantViewSet);
router.register(r'departments', views.DepartmentViewSet)
router.register(r'discounts', views.DiscountViewSet);
router.register(r'discount_uses', views.DiscountUseViewSet);
router.register(r'schools', views.SchoolViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
