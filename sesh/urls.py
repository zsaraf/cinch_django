"""sesh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from apps.university import urls as university_urls
from apps.tutoring import urls as tutoring_urls
from apps.tutor import urls as tutor_urls
from apps.transaction import urls as transaction_urls
from apps.student import urls as student_urls
from apps.notification import urls as notification_urls
from apps.emailclient import urls as emailclient_urls
from apps.account import urls as account_urls
from apps.chatroom import urls as chatroom_urls
from apps.group import urls as group_urls
from apps.tools import urls as tools_urls

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^django/admin/', include(admin.site.urls)),
    url(r'^django/', include(router.urls)),
    url(r'^django/tools/', include(tools_urls)),
    url(r'^django/universities/', include(university_urls)),
    url(r'^django/tutoring/', include(tutoring_urls)),
    url(r'^django/tutors/', include(tutor_urls)),
    url(r'^django/transactions/', include(transaction_urls)),
    url(r'^django/students/', include(student_urls)),
    url(r'^django/notifications/', include(notification_urls)),
    url(r'^django/email-client/', include(emailclient_urls)),
    url(r'^django/accounts/', include(account_urls)),
    url(r'^django/chatrooms/', include(chatroom_urls)),
    url(r'^django/groups/', include(group_urls)),
    url(r'^django/api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
