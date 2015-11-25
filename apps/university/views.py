from rest_framework import viewsets
from apps.university.models import School, Course, Department, Discount, DiscountUse, Constant, BonusPointAllocation
from apps.university.serializers import (
    SchoolSerializer, CourseSerializer, CourseWithGroupsSerializer, DepartmentSerializer, DiscountSerializer, DiscountUseSerializer,
    ConstantSerializer, BonusPointAllocationSerializer
)
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated


class BonusPointAllocationViewSet(viewsets.ModelViewSet):
    queryset = BonusPointAllocation.objects.all()
    serializer_class = BonusPointAllocationSerializer


class CourseViewSet(viewsets.ModelViewSet):
	queryset = Course.objects.all()
	serializer_class = CourseSerializer

	@list_route(methods=['post'], permission_classes=[IsAuthenticated])
	def search(self, request):
		"""
		Get list of classes
		"""
		search_term = request.POST.get('search_term', '')
		courses = Course.objects.search(request.user, search_term)
		obj = CourseWithGroupsSerializer(courses, many=True)
		return Response(obj.data)


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
