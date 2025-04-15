from rest_framework import serializers

from portal.models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            "account_number",
            "user",
            "property",
            "created_at",
        )

        read_only_fields = (
            "id",
            "account_number",
            "created_at",
        )
