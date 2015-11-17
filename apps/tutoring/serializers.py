from apps.tutoring.models import OpenBid, OpenRequest, OpenSesh, PastBid, PastRequest, PastSesh, ReportedProblem
from rest_framework import serializers

class OpenBidSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpenBid

class OpenRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpenRequest

class OpenSeshSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpenSesh

class PastBidSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PastBid

class PastRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PastRequest    
        
class PastSeshSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PastSesh    

class ReportedProblemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ReportedProblem
