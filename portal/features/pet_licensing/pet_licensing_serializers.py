from rest_framework import serializers
from portal.models import PetLicensing


class PetLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetLicensing
        fields = (
            "id",
            "user",
            "property",
            "pet_name",
            "species",
            "breed",
            "age",
            "registration_date",
            "expiration_date",
            "status",
            "fee",
            "vaccination_status",
        )
