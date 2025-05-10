from os import read
import re
from rest_framework import serializers
from portal.models import WaterBill, WaterUsage, BillingDetails, Charges, WaterDebt


class BillingDetailsSerializer(serializers.ModelSerializer):
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
            "rates",
            "water_charges",
            "sewerage",
            "street_lighting",
            "roads_charge",
            "education_levy",
            "total_due",
        )

        read_only_fields = ("total_due", "water_charges")


class WaterUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterUsage
        fields = (
            "previous_reading",
            "current_reading",
            "consumption",
            "date_recorded",
        )

        read_only_fields = (
            "id",
            "consumption",
            "date_recorded",
        )


class WaterDebtSerializer(serializers.ModelSerializer):

    class Meta:
        model = WaterDebt
        fields = (
            "over_90_days",
            "over_60_days",
            "over_30_days",
            "total_debt",
        )

        read_only_fields = (
            "id",
            "total_debt",
        )


class WaterBillSerializer(serializers.ModelSerializer):
    billing_period = BillingDetailsSerializer(many=False)
    water_usage = WaterUsageSerializer(many=False)
    charges = ChargesSerializer(many=False)
    water_debt = WaterDebtSerializer(many=False, required=False, allow_null=True)

    class Meta:
        model = WaterBill
        fields = (
            "id",
            "user",
            "city",
            "bill_number",
            "credit",
            "account",
            "water_usage",
            "charges",
            "water_debt",
            "billing_period",
            "total_amount",
            "amount_paid",
            "remaining_balance",
            "payment_status",
            "created_at",
        )
        read_only_fields = (
            "id",
            "user",
            "city",
            "total_amount",
            "remaining_balance",
            "payment_status",
            "bill_number",
            "created_at",
        )

    def create(self, validated_data):
        billing_period_data = validated_data.pop("billing_period")
        water_usage_data = validated_data.pop("water_usage")
        charges_data = validated_data.pop("charges")
        water_debt_data = validated_data.pop("water_debt", None)

        billing_period = BillingDetails.objects.create(**billing_period_data)
        water_usage = WaterUsage.objects.create(**water_usage_data)
        charges = Charges.objects.create(**charges_data)
        water_debt = (
            WaterDebt.objects.create(**water_debt_data) if water_debt_data else None
        )

        water_bill = WaterBill.objects.create(
            billing_period=billing_period,
            water_usage=water_usage,
            charges=charges,
            water_debt=water_debt,
            **validated_data
        )

        water_bill.calculate_water_charges()
        water_bill.total_amount = water_bill.calculate_total()
        water_bill.save()
        return water_bill

    def update(self, instance, validated_data):
        billing_period_data = validated_data.pop("billing_period", None)
        water_usage_data = validated_data.pop("water_usage", None)
        charges_data = validated_data.pop("charges", None)
        water_debt_data = validated_data.pop("water_debt", None)

        if billing_period_data:
            if not instance.billing_period:
                instance.billing_period = BillingDetails.objects.create(
                    **billing_period_data
                )
            else:
                for attr, value in billing_period_data.items():
                    setattr(instance.billing_period, attr, value)
                instance.billing_period.save()

        if water_usage_data:
            if not instance.water_usage:
                instance.water_usage = WaterUsage.objects.create(**water_usage_data)
            else:
                for attr, value in water_usage_data.items():
                    setattr(instance.water_usage, attr, value)
                instance.water_usage.save()

        if charges_data:
            if not instance.charges:
                instance.charges = Charges.objects.create(**charges_data)
            else:
                for attr, value in charges_data.items():
                    setattr(instance.charges, attr, value)
                instance.charges.save()

        if water_debt_data:
            if not instance.water_debt:
                instance.water_debt = WaterDebt.objects.create(**water_debt_data)
            else:
                for attr, value in water_debt_data.items():
                    setattr(instance.water_debt, attr, value)
                instance.water_debt.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.calculate_water_charges()
        instance.total_amount = instance.calculate_total()
        instance.save()
        return instance
