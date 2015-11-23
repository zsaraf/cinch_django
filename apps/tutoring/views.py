from apps.tutoring.models import OpenBid, OpenRequest, OpenSesh, PastBid, PastRequest, PastSesh, ReportedProblem
from rest_framework import viewsets
from apps.tutoring.serializers import *


class OpenBidViewSet(viewsets.ModelViewSet):
    queryset = OpenBid.objects.all()
    serializer_class = OpenBidSerializer


class OpenRequestViewSet(viewsets.ModelViewSet):
    queryset = OpenRequest.objects.all()
    serializer_class = OpenRequestSerializer


class OpenSeshViewSet(viewsets.ModelViewSet):
    queryset = OpenSesh.objects.all()
    serializer_class = OpenSeshSerializer


class PastBidViewSet(viewsets.ModelViewSet):
    queryset = PastBid.objects.all()
    serializer_class = PastBidSerializer


class PastRequestViewSet(viewsets.ModelViewSet):
    queryset = PastRequest.objects.all()
    serializer_class = PastRequestSerializer


class PastSeshViewSet(viewsets.ModelViewSet):
    queryset = PastSesh.objects.all()
    serializer_class = PastSeshSerializer


class ReportedProblemViewSet(viewsets.ModelViewSet):
    queryset = ReportedProblem.objects.all()
    serializer_class = ReportedProblemSerializer
