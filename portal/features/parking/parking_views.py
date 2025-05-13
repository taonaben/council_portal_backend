from calendar import c
from math import perm

from yaml import serialize
from portal.models import ParkingTicket, ParkingTicketBundle
from portal.features.parking.parking_serializers import (
    ParkingTicketSerializer,
    ParkingSummariesSerializer,
    WeeklyIncomeSerializer,
    TicketBundleDetailSerializer,
    RedeemTicketSerializer,
    TicketBundlePurchaseSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import pagination
from django_redis import get_redis_connection
import json
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.core.cache import cache

# from portal.features.vehicles.vehicle_filters import VehicleReviewFilter, VehicleFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils.timezone import now
from django.db.models import Sum
from datetime import timedelta


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ParkingList(generics.ListCreateAPIView):
    serializer_class = ParkingTicketSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, city=request.user.city)

        response = super().create(request, *args, **kwargs)
        user = request.user
        cache.delete_pattern(
            f"parking_tickets:{user.id}*"
        )  # delete all paginated pages
        return response

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ParkingTicket.objects.filter(city=user.city)
        return ParkingTicket.objects.filter(user=user)

    @method_decorator(cache_control(private=True, max_age=60 * 15))
    def list(self, request, *args, **kwargs):
        user = request.user
        page_number = request.query_params.get("page", 1)
        page_size = request.query_params.get(
            "page_size", self.pagination_class.page_size
        )
        cache_key = f"parking_tickets:{user.id}:page{page_number}:size{page_size}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset().order_by("-issued_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            cache.set(cache_key, response.data, timeout=60 * 15)
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ActiveParkingTicketsView(APIView):
    """
    View to retrieve only active parking tickets for the authenticated user.
    """

    serializer_class = ParkingTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ParkingTicket.objects.filter(user=user, status="active")


class ParkingSummary(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        city = request.user.city
        today = now().date()
        first_day_of_week = today - timedelta(days=today.weekday())
        first_day_of_month = today.replace(day=1)

        summaries = {
            "all_ticket_count": ParkingTicket.objects.filter(city=city).count(),
            "expired_ticket_count": ParkingTicket.objects.filter(
                city=city, status="expired"
            ).count(),
            "paid_ticket_count": ParkingTicket.objects.filter(
                city=city,
            ).count(),
            "daily_ticket_count": ParkingTicket.objects.filter(
                city=city, issued_at__date=today
            ).count(),
            "weekly_ticket_count": ParkingTicket.objects.filter(
                city=city, issued_at__gte=first_day_of_week
            ).count(),
            "monthly_ticket_count": ParkingTicket.objects.filter(
                city=city, issued_at__gte=first_day_of_month
            ).count(),
            "daily_income": ParkingTicket.objects.filter(
                city=city, issued_at__date=today
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0,
            "weekly_income": ParkingTicket.objects.filter(
                city=city, issued_at__gte=first_day_of_week
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0,
            "monthly_income": ParkingTicket.objects.filter(
                city=city, issued_at__gte=first_day_of_month
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0,
        }

        serializer = ParkingSummariesSerializer(summaries)
        return Response(serializer.data)


class WeeklyIncomeParkingSummary(APIView):
    """
    Admin-only view that provides summaries of paid parking tickets,
    including weekly income.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        # Use the serializer to get the total income for each of the last 7 days
        serializer = WeeklyIncomeSerializer()

        weekly_income = serializer.to_representation(
            None
        )  # None because we're not passing an instance

        return Response(weekly_income)


class ParkingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ParkingTicket.objects.all()
    serializer_class = ParkingTicketSerializer
    lookup_url_kwarg = "ticket_id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class VehicleParkingTicketList(generics.ListCreateAPIView):

    serializer_class = ParkingTicketSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = pagination.PageNumberPagination
    # pagination_class.page_size = 2
    pagination_class.page_size_query_param = "page_size"
    max_page_size = 100
    lookup_url_kwarg = "vehicle_id"

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return ParkingTicket.objects.filter(
                user=user, vehicle__id=self.kwargs["vehicle_id"]
            )
        return ParkingTicket.objects.none()


class TicketBundlePurchaseView(generics.CreateAPIView):
    serializer_class = TicketBundlePurchaseSerializer
    permission_classes = [IsAuthenticated]


class RedeemTicketView(generics.CreateAPIView):
    serializer_class = RedeemTicketSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Ensure the user is authenticated
        if not user or not user.is_authenticated:
            return Response({"error": "User not authenticated"}, status=401)

        # Handle pagination parameters with a fallback
        page_number = request.query_params.get("page", 1)
        page_size = request.query_params.get(
            "page_size", getattr(self.pagination_class, "page_size", 10)
        )

        # Construct the cache key
        cache_key = f"ticket_bundles:{user.id}:page{page_number}:size{page_size}"

        # Delete the cache key
        cache.delete(cache_key)

        # Return a success response
        return Response({"message": "Cache cleared successfully"}, status=200)


class TicketBundleListView(generics.ListAPIView):
    serializer_class = TicketBundleDetailSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ParkingTicketBundle.objects.filter(user=self.request.user)

    @method_decorator(cache_control(private=True, max_age=60 * 15))
    def list(self, request, *args, **kwargs):
        user = request.user
        page_number = request.query_params.get("page", 1)
        page_size = request.query_params.get(
            "page_size", self.pagination_class.page_size
        )
        cache_key = f"ticket_bundles:{user.id}:page{page_number}:size{page_size}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset().order_by("-created_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            cache.set(cache_key, response.data, timeout=60 * 15)
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
