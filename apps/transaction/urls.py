from django.conf.urls import include, url
from rest_framework import routers
from apps.transaction import views as transaction_views

router = routers.DefaultRouter()
router.register(r'cash_out_attempts', transaction_views.CashOutAttemptViewSet);
router.register(r'added_online_credits', transaction_views.AddedOnlineCreditViewSet);
router.register(r'outstanding_charges', transaction_views.OutstandingChargeViewSet);

urlpatterns = [
    url(r'^', include(router.urls))
]
