from portal.models import IssueReport
from portal.features.issues.issues_serializers import (
    IssueReportSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from rest_framework.permissions import IsAuthenticated, IsAdminUser

# from portal.features.vehicles.vehicle_filters import VehicleReviewFilter, VehicleFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class issue_list(generics.ListCreateAPIView):
    serializer_class = IssueReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return IssueReport.objects.filter(city=self.request.user.city)

        return IssueReport.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, city=self.request.user.city)


class issue_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = IssueReport.objects.all()
    serializer_class = IssueReportSerializer
    lookup_url_kwarg = "issue_id"
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()
