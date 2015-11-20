from apps.university.models import School, Course, Department, Discount, DiscountUse, Constant, BonusPointAllocation
from rest_framework import serializers


class BonusPointAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusPointAllocation


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course


class ConstantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Constant


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount


class DiscountUseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountUse


class SchoolSerializer(serializers.ModelSerializer):
    line_position = serializers.SerializerMethodField()

    class Meta:
        model = School

    def get_line_position(self, obj):
        return obj.line_position()
