from portal.models import Tax, TaxBill, TaxExemption, TaxPayer
from portal.features.taxes.tax_serializers import (
    TaxSerializer,
    TaxBillSerializer,
    TaxExemptionSerializer,
    TaxPayerSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class tax_list(generics.ListCreateAPIView):
    serializer_class = TaxSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Tax.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = TaxSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class tax_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer
    lookup_url_kwarg = "tax_id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class tax_payer_list(generics.ListCreateAPIView):
    serializer_class = TaxPayerSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):

        return TaxPayer.objects.filter(city=self.request.user.city)

    def post(self, request, *args, **kwargs):
        serializer = TaxPayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class tax_payer_detail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaxPayerSerializer
    lookup_url_kwarg = "tax_payer_id"

    def get_queryset(self):
        return TaxPayer.objects.filter(id=self.kwargs.get("tax_payer_id"))

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class tax_bill_list(generics.ListCreateAPIView):
    serializer_class = TaxBillSerializer

    def get_queryset(self):
        return TaxBill.objects.filter(tax_payer__user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = TaxBillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class tax_bill_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TaxBill.objects.all()
    serializer_class = TaxBillSerializer
    lookup_url_kwarg = "tax_bill_id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class tax_exemption_list(generics.ListCreateAPIView):
    serializer_class = TaxExemptionSerializer

    def get_queryset(self):
        return TaxExemption.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = TaxExemptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class tax_exemption_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TaxExemption.objects.all()
    serializer_class = TaxExemptionSerializer
    lookup_url_kwarg = "tax_exemption_id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()
