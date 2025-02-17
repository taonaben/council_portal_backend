from portal.models import ParkingTicket
from rest_framework import serializers
from django.db.models import Sum
from django.utils.timezone import now


class ParkingTicketSerializer(serializers.ModelSerializer):
    extend_time = serializers.ChoiceField(
        choices=["30min", "1hr", "2hr", "3hr"], required=False, write_only=True
    )

    class Meta:
        model = ParkingTicket
        fields = (
            "id",
            "user",
            "car",
            "city",
            "issued_length",
            "issued_at",
            "expiry_at",
            "amount",
            "status",
            "extend_time",
        )

        extra_kwargs = {
            "extend_time": {"required": False, "write_only": True},
        }

        read_only_fields = (
            "id",
            "user",
            "issued_at",
            "expiry_at",
            "amount",
            "status",
            "city",
        )

    def validate_issued_length(self, value):
        """Ensure the issued_length is a valid choice."""
        if value not in ["30min", "1hr", "2hr", "3hr"]:
            raise serializers.ValidationError("Invalid issued length choice.")
        return value

    def create(self, validated_data):
        validated_data.pop("extend_time", None)  # Remove extend_time before saving

        request = self.context.get("request")
        if request and request.user:
            validated_data["user"] = request.user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Allow extending the ticket if `extend_time` is provided."""
        extend_time = validated_data.pop("extend_time", None)

        if extend_time:
            if instance.status == "expired":
                raise serializers.ValidationError("Cannot extend an expired ticket.")
            instance.extend_ticket(extend_time)  # Calls the model method

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ParkingSummariesSerializer(serializers.ModelSerializer):
    all_ticket_count = serializers.SerializerMethodField()
    expired_ticket_count = serializers.SerializerMethodField()
    paid_ticket_count = serializers.SerializerMethodField()
    daily_income = serializers.SerializerMethodField()
    monthly_income = serializers.SerializerMethodField()

    def get_all_ticket_count(self, obj):
        return ParkingTicket.objects.filter(city=obj.user.city).count()

    def get_expired_ticket_count(self, obj):
        return ParkingTicket.objects.filter(
            city=obj.user.city, status="expired"
        ).count()

    def get_paid_ticket_count(self, obj):
        return ParkingTicket.objects.filter(city=obj.user.city, status="paid").count()

    def get_daily_income(self, obj):
        today = now().date()
        total_income = ParkingTicket.objects.filter(
            city=obj.user.city, status="paid", issued_at__date=today
        ).aggregate(total_income=Sum("amount"))["total_income"]
        return total_income or 0

    def get_monthly_income(self, obj):
        first_day_of_month = now().replace(day=1)
        total_income = ParkingTicket.objects.filter(
            city=obj.user.city, status="paid", issued_at__gte=first_day_of_month
        ).aggregate(total_income=Sum("amount"))["total_income"]
        return total_income or 0

    class Meta:
        model = ParkingTicket
        fields = (
            "all_ticket_count",
            "expired_ticket_count",
            "paid_ticket_count",
            "daily_income",
            "monthly_income",
        )
