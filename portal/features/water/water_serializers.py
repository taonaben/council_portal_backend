from pyexpat import model
from turtle import mode
from rest_framework import serializers
from portal.models import (
    WaterBill,
    WaterMeter,
    WaterUsage,
    Account,
    BillingPeriod,
    Charges,
    PaymentDetails,
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


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            "account_number",
            "name",
            "address",
        )


class BillingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingPeriod
        fields = (
            "last_receipt_date",
            "bill_date",
            "due_date",
        )


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


class PaymentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetails
        fields = (
            "pay_before_or_on",
            "amount_due",
            "vat_inclusive",
        )


class WaterBillSerializer(serializers.ModelSerializer):

    account = AccountSerializer(many=False)
    billing_period = BillingPeriodSerializer(many=False)
    charges = ChargesSerializer(many=False)
    payment_details = PaymentDetailsSerializer(many=False)

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

        read_only_fields = (
            "id",
            "user",
            "account",
            "bill_number",
            "charges",
            "payment_details",
            "billing_period",
            "created_at",
        )


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
