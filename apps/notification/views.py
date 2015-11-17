from apps.notification.models import NotificationType, OpenNotification, PastNotification
from rest_framework import viewsets
from apps.notification.serializers import NotificationTypeSerializer, OpenNotificationSerializer, PastNotificationSerializer

class NotificationTypeViewSet(viewsets.ModelViewSet):
    queryset = NotificationType.objects.all()
    serializer_class = NotificationTypeSerializer
    
class OpenNotificationViewSet(viewsets.ModelViewSet):
    queryset = OpenNotification.objects.all()
    serializer_class = OpenNotificationSerializer
    
class PastNotificationViewSet(viewsets.ModelViewSet):
    queryset = PastNotification.objects.all()
    serializer_class = PastNotificationSerializer