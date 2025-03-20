from os import read
from rest_framework import serializers
from portal.features.user_accounts.account_serializer import AccountSerializer
from portal.models import (
    WaterBill,
    WaterMeter,
    WaterUsage,
    Account,
    BillingDetails,
    Charges,
)
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


class BillingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingDetails
        fields = (
            "last_receipt_date",
            "bill_date",
            "due_date",
        )

        # read_only_fields = ("last_receipt_date", "bill_date", "due_date")


class ChargesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charges
        fields = (
            "balance_forward",
            "water_charges",
            "sewerage",
            "street_lighting",
            "roads_charge",
            "education_levy",
            "total_due",
        )

        read_only_fields = ("total_due",)


class WaterBillSerializer(serializers.ModelSerializer):

    account_number = serializers.CharField()  # New field
    billing_period = BillingPeriodSerializer(many=False)
    charges = ChargesSerializer(many=False)

    class Meta:
        model = WaterBill
        fields = (
            "id",
            "user",
            "account_number",  # New field
            "city",
            "bill_number",
            "charges",
            "billing_period",
            "created_at",
        )

        read_only_fields = (
            "id",
            "bill_number",
            "charges",
            "billing_period",
            "created_at",
        )

    def create(self, validated_data):
        billing_period_data = validated_data.pop("billing_period")
        charges_data = validated_data.pop("charges")

        billing_period = BillingDetails.objects.create(**billing_period_data)
        charges = Charges.objects.create(**charges_data)

        water_bill = WaterBill.objects.create(
            billing_period=billing_period,
            charges=charges,
            **validated_data
        )
        return water_bill


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
