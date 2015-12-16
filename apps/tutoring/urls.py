from django.conf.urls import include, url
from rest_framework import routers
from apps.tutoring import views as tutoring_views

router = routers.DefaultRouter()
router.register(r'open_bids', tutoring_views.OpenBidViewSet)
router.register(r'sesh_requests', tutoring_views.SeshRequestViewSet)
router.register(r'open_seshes', tutoring_views.OpenSeshViewSet)
router.register(r'past_bids', tutoring_views.PastBidViewSet)
router.register(r'past_seshes', tutoring_views.PastSeshViewSet)
router.register(r'reported_problems', tutoring_views.ReportedProblemViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
