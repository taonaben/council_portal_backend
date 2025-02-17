from portal.models import Business, BusinessLicense, BusinessLicenseApproval
from portal.features.business.business_serializers import (
    BusinessSerializer,
    BusinessLicenseSerializer,
    BusinessLicenseApprovalSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from rest_framework.permissions import IsAuthenticated, IsAdminUser

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class business_list(generics.ListCreateAPIView):
    serializer_class = BusinessSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.user.is_staff:
            return Business.objects.filter(city_registered=self.request.user.city)
        else:
            return Business.objects.filter(owner=self.request.user)
        
    

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user,
            city_registered=self.request.user.city,
        )


class business_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    lookup_url_kwarg = "business_id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class business_license_list(generics.ListCreateAPIView):
    serializer_class = BusinessLicenseSerializer

    def get_queryset(self):
        business_id = self.kwargs.get("business_id")
        return BusinessLicense.objects.filter(business_id=business_id)

    def perform_create(self, serializer):
        return super().perform_create(serializer)


class business_license_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BusinessLicense.objects.all()
    serializer_class = BusinessLicenseSerializer
    lookup_url_kwarg = "business_license_id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class business_license_approval_list(generics.ListAPIView):
    serializer_class = BusinessLicenseApprovalSerializer

    def get_permissions(self):
        self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        # business_license_id = self.kwargs.get("business_license_id")
        return BusinessLicenseApproval.objects.filter(
            license__business__city_registered=self.request.user.city
        )


class business_license_approval_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BusinessLicenseApproval.objects.all()
    serializer_class = BusinessLicenseApprovalSerializer
    lookup_url_kwarg = "business_license_approval_id"

    def get_permissions(self):
        self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = BusinessLicenseApprovalSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save(admin=self.request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = BusinessLicenseApprovalSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save(admin=self.request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

