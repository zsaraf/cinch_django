from django.conf.urls import include, url
from rest_framework import routers
from . import views

chatroom_activity_vs = views.ChatroomActivityViewSet.as_view({
    'get': 'retrieve',
    'post': 'retrieve'
})

router = routers.DefaultRouter()
router.register(r'announcements', views.AnnouncementViewSet)
router.register(r'chatrooms', views.ChatroomViewSet)
router.register(r'chatroom_activity', views.ChatroomActivityViewSet)
router.register(r'chatroom_activity_types', views.ChatroomActivityTypeViewSet)
router.register(r'files', views.FileViewSet)
router.register(r'uploads', views.UploadViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'interactions', views.InteractionViewSet)

urlpatterns = [
    url(r'^chatroom_activity/(?P<pk>[0-9]+)/$', chatroom_activity_vs, name='chatroom-activity-vs'),
    url(r'^', include(router.urls))
]
