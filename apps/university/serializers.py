from apps.university.models import School, Class, Department, Discount, DiscountUse, Constant, BonusPointAllocation
from rest_framework import serializers

class BonusPointAllocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BonusPointAllocation

class ClassSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Class

class ConstantSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Constant
        
class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Department
        
class DiscountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Discount
        
class DiscountUseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DiscountUse
        
class SchoolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = School