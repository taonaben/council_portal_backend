from portal.models import ParkingTicket
from portal.features.parking.parking_serializers import (
    ParkingTicketSerializer,
    ParkingSummariesSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser

# from portal.features.vehicles.vehicle_filters import VehicleReviewFilter, VehicleFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

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


class ParkingSummary(generics.ListAPIView):
    """
    Admin-only view that provides summaries of paid parking tickets,
    including daily and monthly income.
    """

    serializer_class = ParkingSummariesSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return ParkingTicket.objects.filter(city=self.request.user.city)


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
