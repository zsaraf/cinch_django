from django.shortcuts import render
from rest_framework import viewsets
from apps.university.models import School, Class, Department, Discount, DiscountUse, Constant, BonusPointAllocation
from apps.university.serializers import SchoolSerializer, ClassSerializer, DepartmentSerializer, DiscountSerializer, DiscountUseSerializer, ConstantSerializer, BonusPointAllocationSerializer

class BonusPointAllocationViewSet(viewsets.ModelViewSet):
	queryset = BonusPointAllocation.objects.all()
	serializer_class = BonusPointAllocationSerializer

class ClassViewSet(viewsets.ModelViewSet):
	queryset = Class.objects.all()
	serializer_class = ClassSerializer
	
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