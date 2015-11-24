from apps.university.models import School, Course, Department, Discount, DiscountUse, Constant, BonusPointAllocation
from rest_framework import serializers

class BonusPointAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusPointAllocation

class CourseWithGroupsSerializer(serializers.ModelSerializer):
    course_groups = serializers.SerializerMethodField()

    class Meta:
        model = Course

    def get_course_groups(self, obj):
        from apps.group.serializers import CourseGroupBasicSerializer
        from apps.group.models import CourseGroup
        return CourseGroupBasicSerializer(CourseGroup.objects.filter(course__id__exact=obj.pk), many=True).data

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
    line_position = serializers.ReadOnlyField()

    class Meta:
        model = School
