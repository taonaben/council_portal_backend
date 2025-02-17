from portal.models import City, CitySection

from rest_framework import serializers

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = (
            'id',
            'name',
        )

        read_only_fields = ('id',)

    
class CitySectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CitySection
        fields = (
            'city',
            'name',
            'section',
        )