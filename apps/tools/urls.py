from django.conf.urls import url
from apps.tools import views


urlpatterns = [
    url(r'leaderboard', views.Leaderboard.as_view(), name='leaderboard'),
    url(r'dashboard', views.Dashboard.as_view(), name='dashboard'),
    url(r'chat', views.TeamChat.as_view(), name='chat'),
    url(r'course_groups', views.CourseGroupDash.as_view(), name='course_groups'),
    url(r'merge', views.MergeCourseGroups.as_view(), name='merge')
]
