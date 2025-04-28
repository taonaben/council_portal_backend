from calendar import weekday
from datetime import timedelta, timezone, datetime
from portal.models import ParkingTicket
from rest_framework import serializers
from django.db.models import Sum
from django.utils import timezone


class ParkingTicketSerializer(serializers.ModelSerializer):
    extend_time = serializers.ChoiceField(
        choices=["30min", "1hr", "2hr", "3hr"], required=False, write_only=True
    )

    class Meta:
        model = ParkingTicket
        fields = (
            "id",
            "ticket_number",
            "user",
            "vehicle",
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
            "ticket_number",
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
        activate_ticket = validated_data.pop("activate_ticket", None)

        if extend_time:
            if instance.status == "expired":
                raise serializers.ValidationError("Cannot extend an expired ticket.")
            instance.extend_ticket(extend_time)  # Calls the model method

        if activate_ticket:
            instance.activate_ticket()  # Calls the model method
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ParkingSummariesSerializer(serializers.Serializer):
    all_ticket_count = serializers.IntegerField()
    expired_ticket_count = serializers.IntegerField()
    paid_ticket_count = serializers.IntegerField()
    daily_ticket_count = serializers.IntegerField()
    weekly_ticket_count = serializers.IntegerField()
    monthly_ticket_count = serializers.IntegerField()
    daily_income = serializers.FloatField()
    weekly_income = serializers.FloatField()
    monthly_income = serializers.FloatField()

    class Meta:
        fields = [
            "all_ticket_count",
            "expired_ticket_count",
            "paid_ticket_count",
            "daily_ticket_count",
            "weekly_ticket_count",
            "monthly_ticket_count",
            "daily_income",
            "weekly_income",
            "monthly_income",
        ]


# get revenue of the week of each day


class IncomeSummarySerializer(serializers.Serializer):
    date = serializers.DateField()
    total_income = serializers.FloatField()


class WeeklyIncomeSerializer(serializers.ModelSerializer):
    date = serializers.DateField()
    total_income = serializers.FloatField()

    class Meta:
        model = ParkingTicket
        fields = ("date", "total_income")

    @staticmethod
    def get_income_by_day():
        # Get the current date
        today = timezone.now().date()

        # Calculate the total income for each of the last 7 days, including today
        weekly_income = []
        for i in range(7):
            day = today - timedelta(days=i)  # Get the date for this day
            income = (
                ParkingTicket.objects.filter(issued_at__date=day).aggregate(
                    total_income=Sum("amount")
                )["total_income"]
                or 0
            )
            weekly_income.append({"date": day, "total_income": income})

        return weekly_income

    def to_representation(self, instance):
        # Return the daily income list as a response
        data = self.get_income_by_day()
        return data


# get the daily hourly revenue

# get total daily ticket count
