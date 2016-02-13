from django.conf.urls import url
from apps.tools import views

urlpatterns = [
    url(r'leaderboard', views.Leaderboard.as_view(), name='leaderboard'),
    url(r'dashboard', views.Dashboard.as_view(), name='dashboard'),
    url(r'team_chat', views.TeamChat.as_view(), name='team_chat')
]
