from apps.transaction.models import AddedOnlineCredit, OutstandingCharge, CashOutAttempt
from rest_framework import viewsets
from apps.transaction.serializers import OutstandingChargeSerializer, AddedOnlineCreditSerializer, CashOutAttemptSerializer

class CashOutAttemptViewSet(viewsets.ModelViewSet):
    queryset = CashOutAttempt.objects.all()
    serializer_class = CashOutAttemptSerializer

class AddedOnlineCreditViewSet(viewsets.ModelViewSet):
    queryset = AddedOnlineCredit.objects.all()
    serializer_class = AddedOnlineCreditSerializer

class OutstandingChargeViewSet(viewsets.ModelViewSet):
    queryset = OutstandingCharge.objects.all()
    serializer_class = OutstandingChargeSerializer


