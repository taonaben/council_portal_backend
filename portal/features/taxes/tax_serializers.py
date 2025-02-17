from datetime import timezone
from rest_framework import serializers
from portal.models import Tax, TaxBill, TaxExemption, TaxPayer, City


class TaxSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        city_name = City.objects.get(id=instance.city_id).name
        representation = super().to_representation(instance)
        if instance.type == "residential" and instance.city == city_name:
            if instance.property_value >= 100000:
                representation["rate"] = 1
            else:
                representation["rate"] = instance.rate
        return representation

    class Meta:
        model = Tax
        fields = (
            "id",
            "city",
            "type",
            "rate",
            "renewal_period",
            "description",
        )

        extra_kwargs = {
            "id": {"read_only": True},
        }


class TaxPayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxPayer
        fields = (
            "id",
            "user",
            "city",
            "property",
            "business",
            "vehicle",
            "total_tax_due",
            "last_payment_date",
        )

        extra_kwargs = {
            "id": {"read_only": True},
        }


class TaxExemptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxExemption
        fields = (
            "id",
            "tax",
            "taxpayer",
            "exemption_reason",
            "discount_rate",
        )

        extra_kwargs = {
            "id": {"read_only": True},
        }


class TaxBillSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if (
            data["due_date"] < timezone.now().date()
            and data["amount_paid"] < data["amount_due"]
        ):
            data["status"] = "overdue"
        elif data["amount_paid"] >= data["amount_due"]:
            data["status"] = "paid"
        else:
            data["status"] = "pending"
        return data

    class Meta:
        model = TaxBill
        fields = (
            "id",
            "tax_payer",
            "tax",
            "amount_due",
            "amount_paid",
            "due_date",
            "status",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "status": {"read_only": True},
        }
