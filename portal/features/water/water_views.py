from portal.models import WaterBill, WaterMeter, WaterUsage
from portal.features.water.water_serializers import (
    WaterBillSerializer,
    WaterMeterSerializer,
    WaterUsageSerializer,
)

from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import viewsets


class WaterMeterView(viewsets.ModelViewSet):
    queryset = WaterBill.objects.all()
    serializer_class = WaterMeterSerializer


class WaterBillView(viewsets.ModelViewSet):
    queryset = WaterBill.objects.all()
    serializer_class = WaterBillSerializer


class WaterUsageView(viewsets.ModelViewSet):
    queryset = WaterUsage.objects.all()
    serializer_class = WaterUsageSerializer
