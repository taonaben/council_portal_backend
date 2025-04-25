from rest_framework import serializers

from portal.models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            "account_number",
            "user",
            "property",
            "water_meter_number",
            "created_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )
