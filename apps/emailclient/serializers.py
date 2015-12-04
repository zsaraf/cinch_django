from apps.emailclient.models import PendingEmail
from rest_framework import serializers


class PendingEmailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PendingEmail
