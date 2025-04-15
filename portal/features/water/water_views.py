from portal.models import WaterBill, WaterMeter, WaterUsage
from portal.features.water.water_serializers import (
    WaterBillSerializer,
    WaterMeterSerializer,
    WaterUsageSerializer,
    TotalWaterDebtSerializer,
)

from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import viewsets

from rest_framework.permissions import IsAuthenticated, IsAdminUser

# from portal.features.vehicles.vehicle_filters import VehicleReviewFilter, VehicleFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class water_meter_list(generics.ListCreateAPIView):
    serializer_class = WaterMeterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return WaterMeter.objects.filter(property__city=self.request.user.city)

        return WaterMeter.objects.filter(property__owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class water_meter_detail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WaterMeterSerializer
    lookup_url_kwarg = "meter_id"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WaterMeter.objects.filter(id=self.kwargs.get("meter_id"))

    def delete(self, request, *args, **kwargs):
        if request.user.is_staff:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        if request.user.is_staff:
            instance = self.get_object()
            serializer = WaterMeterSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, *args, **kwargs):
        if request.user.is_staff:
            instance = self.get_object()
            serializer = WaterMeterSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def perform_update(self, serializer):
        return serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


class water_usage_list(generics.ListAPIView):
    serializer_class = WaterUsageSerializer
    permission_classes = [IsAuthenticated]
    queryset = WaterUsage.objects.none()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return WaterUsage.objects.filter(property__owner=self.request.user)
        return WaterUsage.objects.all()


class water_usage_detail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WaterUsageSerializer
    lookup_url_kwarg = "usage_id"

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WaterUsage.objects.filter(id=self.kwargs.get("usage_id"))

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class water_bill_list(generics.ListCreateAPIView):

    serializer_class = WaterBillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return WaterBill.objects.filter(city=self.request.user.city)

        return WaterBill.objects.filter(property__owner=self.request.user)


class water_bill_detail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WaterBillSerializer
    lookup_url_kwarg = "water_bill_id"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WaterBill.objects.filter(id=self.kwargs.get("water_bill_id"))

class total_water_debt(generics.ListAPIView):

    serializer_class = TotalWaterDebtSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return WaterBill.objects.filter(property__city=self.request.user.city)

        return WaterBill.objects.filter(property__owner=self.request.user)