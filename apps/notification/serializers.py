from apps.notification.models import NotificationType, OpenNotification, PastNotification
from rest_framework import serializers

class NotificationTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NotificationType

class OpenNotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpenNotification

class PastNotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PastNotification
