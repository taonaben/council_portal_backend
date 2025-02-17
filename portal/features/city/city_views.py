from portal.models import City, CitySection
from portal.features.city.city_serializers import CitySerializer, CitySectionSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import generics


class cities_list(generics.ListCreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class city_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    lookup_url_kwarg = 'pk'

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        instance.delete()

class city_sections_list(generics.ListCreateAPIView):
    serializer_class = CitySectionSerializer
    
    def get_queryset(self):
        city_id = self.kwargs.get('city_id')
        return CitySection.objects.filter(city_id=city_id)

class city_section_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CitySection.objects.all()
    serializer_class = CitySectionSerializer
    lookup_url_kwarg = 'pk'

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        instance.delete()
