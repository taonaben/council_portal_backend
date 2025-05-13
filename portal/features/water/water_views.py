from portal.models import WaterBill
from portal.features.water.water_serializers import WaterBillSerializer

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from rest_framework.permissions import IsAuthenticated, IsAdminUser

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django_redis import get_redis_connection
import json
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.core.cache import cache

from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CreateWaterBillView(generics.CreateAPIView):
    serializer_class = WaterBillSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, city=request.user.city)

        response = super().create(request, *args, **kwargs)
        user = request.user
        cache.delete_pattern(f"water_bills:{user.id}*")  # delete all paginated pages
        return response


class WaterBillListAll(generics.ListAPIView):
    serializer_class = WaterBillSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user

        base_queryset = WaterBill.objects.select_related(
            "user",
            "account",
            "city",
            "billing_period",
            "water_usage",
            "charges",
            "water_debt",
        ).prefetch_related("account__property")

        if user.is_staff:
            return base_queryset.filter(city=user.city)
        return base_queryset.filter(user=user)

    @method_decorator(cache_control(private=True, max_age=60 * 15))
    def list(self, request, *args, **kwargs):
        user = request.user
        page_number = request.query_params.get("page", 1)
        page_size = request.query_params.get(
            "page_size", self.pagination_class.page_size
        )
        cache_key = f"water_bills:{user.id}:page{page_number}:size{page_size}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset().order_by("-created_at")
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        response = self.get_paginated_response(serializer.data)

        cache.set(cache_key, response.data, timeout=60 * 15)
        return response


class WaterBillListByAccount(generics.ListAPIView):
    serializer_class = WaterBillSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        account_id = self.kwargs.get("account_id")
        if not account_id:
            raise ValidationError({"detail": "Account ID is required."})

        base_queryset = WaterBill.objects.select_related(
            "user",
            "account",
            "city",
            "billing_period",
            "water_usage",
            "charges",
            "water_debt",
        ).prefetch_related("account__property")

        if self.request.user.is_staff:
            return base_queryset.filter(city=self.request.user.city, account=account_id)
        return base_queryset.filter(user=self.request.user, account=account_id)

    @method_decorator(cache_control(private=True, max_age=60 * 15))
    def list(self, request, *args, **kwargs):
        user = request.user
        account_id = self.kwargs.get("account_id")
        page_number = request.query_params.get("page", 1)
        page_size = request.query_params.get(
            "page_size", self.pagination_class.page_size
        )

        cache_key = f"water_bills:{user.id}:account:{account_id}:page{page_number}:size{page_size}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset().order_by("-created_at")
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        response = self.get_paginated_response(serializer.data)

        cache.set(cache_key, response.data, timeout=60 * 15)
        return response


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
            amount_paid = request.data.get("amount_paid", 0)
            if amount_paid:
                instance.amount_paid += float(amount_paid)
                instance.remaining_balance = instance.get_remaining_balance()
                instance.update_payment_status()
                instance.save()
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = WaterBillSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            amount_paid = request.data.get("amount_paid", 0)
            if amount_paid:
                instance.amount_paid += float(amount_paid)
                instance.remaining_balance = instance.get_remaining_balance()
                instance.update_payment_status()
                instance.save()
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LatestWaterBillView(generics.RetrieveAPIView):
    serializer_class = WaterBillSerializer
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_control(private=True, max_age=60 * 15))
    def retrieve(self, request, *args, **kwargs):
        user = request.user
        account_id = self.kwargs.get("account_id")
        cache_key = f"latest_water_bill:{user.id}:account:{account_id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        obj = self.get_object()
        serializer = self.get_serializer(obj)
        cache.set(cache_key, serializer.data, timeout=60 * 15)
        return Response(serializer.data)

    def get_object(self):
        account_id = self.kwargs.get("account_id")
        return (
            WaterBill.objects.filter(user=self.request.user, account=account_id)
            .select_related(
                "account",
                "city",
                "billing_period",
                "water_usage",
                "charges",
                "water_debt",
            )
            .order_by("-created_at")
            .first()
        )
