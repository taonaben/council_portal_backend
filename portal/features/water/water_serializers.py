from rest_framework import serializers
from portal.models import WaterBill, WaterMeter, WaterUsage
from django.db.models import Sum


class WaterMeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterMeter
        fields = (
            "id",
            "meter_num",
            "property",
            "current_reading",
        )

        read_only_fields = ("id", "current_reading", "meter_num")

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
            "id",
            "user",
            "account",
            "city",
            "bill_number",
            "charges",
            "payment_details",
            "billing_period",
            "created_at",
        )

        # read_only_fields = (
        #     "id",
        #     "user",
        #     "account",
        #     "bill_number",
        #     "charges",
        #     "payment_details",
        #     "billing_period",
        #     "created_at",
        # )


class TotalWaterDebtSerializer(serializers.Serializer):
    total_amount_owed = serializers.SerializerMethodField(
        method_name="get_total_amount_owed"
    )

    def get_total_amount_owed(self, obj) -> float:
        return (
            WaterBill.objects.aggregate(total_owed=Sum("amount_owed"))["total_owed"]
            or 0
        )

    class Meta:
        fields = ("total_amount_owed",)
