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
from django_redis import get_redis_connection

import json
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.core.cache import cache


def _convert_uuids_to_str(data):
    if isinstance(data, dict):
        return {k: _convert_uuids_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_convert_uuids_to_str(i) for i in data]
    elif hasattr(data, "hex") and hasattr(data, "int"):
        # Likely a UUID
        return str(data)
    return data


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

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Vehicle.objects.filter(city_registered=user.city)
        return Vehicle.objects.filter(owner=user)

    @method_decorator(cache_control(private=True, max_age=60 * 15))
    def list(self, request, *args, **kwargs):
        user = request.user
        cache_key = f"vehicles:{user.id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(json.loads(cached_data))

        queryset = self.get_queryset().order_by("-registered_at")[:5]
        serializer = self.get_serializer(queryset, many=True)
        data = _convert_uuids_to_str(serializer.data)

        cache.set(cache_key, json.dumps(data), timeout=60 * 15)
        return Response(data)

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
