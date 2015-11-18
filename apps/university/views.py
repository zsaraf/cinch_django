from django.shortcuts import render
from rest_framework import viewsets
from apps.university.models import School, Course, Department, Discount, DiscountUse, Constant, BonusPointAllocation
from apps.university.serializers import SchoolSerializer, CourseSerializer, DepartmentSerializer, DiscountSerializer, DiscountUseSerializer, ConstantSerializer, BonusPointAllocationSerializer

class BonusPointAllocationViewSet(viewsets.ModelViewSet):
	queryset = BonusPointAllocation.objects.all()
	serializer_class = BonusPointAllocationSerializer

class CourseViewSet(viewsets.ModelViewSet):
	queryset = Course.objects.all()
	serializer_class = CourseSerializer
	
class ConstantViewSet(viewsets.ModelViewSet):
	queryset = Constant.objects.all()
	serializer_class = ConstantSerializer
	
class DepartmentViewSet(viewsets.ModelViewSet):
	queryset = Department.objects.all()
	serializer_class = DepartmentSerializer
    
class DiscountViewSet(viewsets.ModelViewSet):
	queryset = Discount.objects.all()
	serializer_class = DiscountSerializer
    
class DiscountUseViewSet(viewsets.ModelViewSet):
	queryset = DiscountUse.objects.all()
	serializer_class = DiscountUseSerializer

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer