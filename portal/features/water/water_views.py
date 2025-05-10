from portal.models import WaterBill
from portal.features.water.water_serializers import WaterBillSerializer

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated, IsAdminUser

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class water_bill_list(generics.ListCreateAPIView):
    serializer_class = WaterBillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        base_queryset = WaterBill.objects.select_related(
            "user",
            "account",
            "city",
            "billing_period",
            "water_usage",
            "charges",
            "water_debt",
        ).prefetch_related(
            "account__property",
        )

        if self.request.user.is_staff:
            return base_queryset.filter(city=self.request.user.city)

        return base_queryset.filter(property__owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, city=self.request.user.city)


class water_bill_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = WaterBill.objects.all()
    serializer_class = WaterBillSerializer
    lookup_url_kwarg = "water_bill_id"
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = WaterBillSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = WaterBillSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class latest_water_bill(generics.RetrieveAPIView):
    serializer_class = WaterBillSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve the latest water bill for the authenticated user
        return (
            WaterBill.objects.filter(user=self.request.user)
            .order_by("-created_at")
            .first()
        )
