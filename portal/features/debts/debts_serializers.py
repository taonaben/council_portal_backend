from rest_framework import serializers
from portal.models import Debt


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = (
            "id",
            "user",
            "property",
            "bill",
            "amount_owed",
            "amount_paid",
            "due_date",
            "status",
            "last_payment_date",
        )
