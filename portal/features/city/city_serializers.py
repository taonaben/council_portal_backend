from portal.models import City, CitySection

from rest_framework import serializers


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = (
            "id",
            "name",
            "sections",
            "latitude",
            "longitude",
        )

        read_only_fields = ("id", "sections")


class CitySectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CitySection
        fields = (
            "city",
            "name",
            "density",
        )
