from rest_framework import serializers
from portal.models import WaterBill, WaterMeter, WaterUsage


class WaterMeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterMeter
        fields = "__all__"

    def update(self, instance, validated_data):
        new_reading = validated_data.get("current_reading", instance.current_reading)
        instance.update_reading(new_reading)
        return instance


class WaterUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterUsage
        fields = (
            "id",
            "meter",
            "property",
            "consumption",
            "date_recorded",
        )

        extra_kwargs = {
            "id": {"read_only": True},
        }


class WaterBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterBill
        fields = (
            'id',
            'property',
            'water_used',
            'meter_number',
            'amount'
        )

        extra_kwargs = {
            "id": {"read_only": True},
        }
