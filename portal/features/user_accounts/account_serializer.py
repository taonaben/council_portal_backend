from rest_framework import serializers

from portal.models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            "id",
            "account_number",
            "user",
            "property",
            "water_meter_number",
            "created_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "account_number",
            "water_meter_number",
        )
