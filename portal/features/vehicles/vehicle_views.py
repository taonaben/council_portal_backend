from portal.models import Vehicle, VehicleApproval
from portal.features.vehicles.vehicle_serializers import (
    VehicleSerializer,
    VehicleApprovalSerializer,
)
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from portal.features.vehicles.vehicle_filters import VehicleReviewFilter, VehicleFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class VehicleList(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filterset_class = VehicleFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "owner__first_name",
        "owner__last_name",
        "plate_number",
    ]

    def get_query_set(self):
        if self.request.user.is_staff:
            return Vehicle.objects.filter(city_registered=self.request.user.city)
        else:
            return Vehicle.objects.filter(owner=self.request.user)

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAuthenticated]
        return super(VehicleList, self).get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, city_registered=self.request.user.city)


class VehicleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    lookup_url_kwarg = "vehicle_id"

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = VehicleSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = VehicleSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VehicleReviewList(generics.ListAPIView):
    serializer_class = VehicleApprovalSerializer
    filterset_class = VehicleReviewFilter  
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "vehicle__owner__first_name",
        "vehicle__owner__last_name",
        "vehicle__plate_number",
        "vehicle__id",
    ]

    def get_queryset(self):
        self.queryset = VehicleApproval.objects.filter(
            vehicle__city_registered=self.request.user.city
        )
        # self.queryset = VehicleApproval.objects.all()
        return super().get_queryset()

    def get_permissions(self):
        self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    # def perform_create(self, serializer):
    #     serializer.save(admin=self.request.user)


class VehicleReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = VehicleApproval.objects.all()
    serializer_class = VehicleApprovalSerializer
    lookup_url_kwarg = "vehicle_review_id"

    def get_permissions(self):
        self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = VehicleApprovalSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save(admin=self.request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = VehicleSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(admin=self.request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
