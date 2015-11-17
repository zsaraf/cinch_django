from apps.transaction.models import CashOutAttempt, AddedOnlineCredit, OutstandingCharge
from rest_framework import serializers

class CashOutAttemptSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CashOutAttempt

class AddedOnlineCreditSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AddedOnlineCredit

class OutstandingChargeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OutstandingCharge