from django.shortcuts import render
from rest_framework import viewsets
from apps.emailclient.models import PendingEmail
from apps.emailclient.serializers import PendingEmailSerializer

class PendingEmailViewSet(viewsets.ModelViewSet):
	queryset = PendingEmail.objects.all()
	serializer_class = PendingEmailSerializer
