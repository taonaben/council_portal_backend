from portal.models import City, CitySection
from portal.features.city.city_serializers import CitySerializer, CitySectionSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import generics

from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny


class cities_list(generics.ListCreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class city_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    lookup_url_kwarg = "city_id"
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        if request.user.is_superuser:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def perform_destroy(self, instance):
        instance.delete()


class city_sections_list(generics.ListCreateAPIView):
    serializer_class = CitySectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CitySection.objects.filter(city=self.request.user.city)

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class city_section_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CitySection.objects.all()
    serializer_class = CitySectionSerializer
    lookup_url_kwarg = "section_id"
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        if request.user.is_superuser:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def perform_destroy(self, instance):
        instance.delete()
