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

# from portal.features.vehicles.vehicle_filters import VehicleReviewFilter, VehicleFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils.timezone import now
from django.db.models import Sum
from datetime import timedelta

"""
    PERMISSIONS

    for admin:
        delete ticket
        view all user tickets in city
        view summaries of paid tickets(daily income, monthly income, number of tickets paid)

    for user:
        add ticket
        edit ticket(add more time)
        view personal tickets of all their cars



    
"""


class ParkingList(generics.ListCreateAPIView):
    """
    Handles:
    - Listing user-specific tickets (for normal users)
    - Listing all tickets in a city (for admins)
    - Creating new tickets (for authenticated users)
    """

    serializer_class = ParkingTicketSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = pagination.PageNumberPagination
    # pagination_class.page_size = 2
    pagination_class.page_size_query_param = "page_size"
    max_page_size = 100

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:  # Admins see all tickets in their city
                return ParkingTicket.objects.filter(city=user.city)
            return ParkingTicket.objects.filter(
                user=user
            )  # Users see only their tickets
        return ParkingTicket.objects.none()

    def perform_create(self, serializer):
        extend_time = self.request.data.get("extend_time")
        ticket = serializer.save(user=self.request.user, city=self.request.user.city)

        if extend_time:
            ticket.extend_ticket(extend_time)
            ticket.save()


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


class TicketBundleListView(generics.ListAPIView):
    serializer_class = TicketBundleDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ParkingTicketBundle.objects.filter(user=self.request.user)
