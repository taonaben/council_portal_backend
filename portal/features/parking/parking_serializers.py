from calendar import weekday
from datetime import timedelta, timezone, datetime
from portal.models import ParkingTicket, ParkingTicketBundle, City, Vehicle
from rest_framework import serializers
from django.db.models import Sum, F
from django.utils import timezone


class ParkingTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParkingTicket
        fields = (
            "id",
            "ticket_number",
            "user",
            "vehicle",
            "city",
            "issued_at",
            "minutes_issued",
            "expiry_at",
            "amount",
            "status",
        )

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

    def create(self, validated_data):

        request = self.context.get("request")
        if request and request.user:
            validated_data["user"] = request.user

        return super().create(validated_data)


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


# serializers.py
class TicketBundlePurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingTicketBundle
        fields = ["id", "quantity", "ticket_minutes", "price_paid"]

    def create(self, validated_data):
        user = self.context["request"].user
        return ParkingTicketBundle.objects.create(user=user, **validated_data)


class RedeemTicketSerializer(serializers.Serializer):
    vehicle_id = serializers.UUIDField()
    city_id = serializers.UUIDField()

    def validate(self, data):
        user = self.context["request"].user
        bundle = (
            ParkingTicketBundle.objects.filter(
                user=user, quantity__gt=F("tickets_redeemed")
            )
            .order_by("purchased_at")
            .first()
        )

        if not bundle:
            raise serializers.ValidationError("No available ticket bundles to redeem.")

        data["bundle"] = bundle
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        vehicle_id = validated_data["vehicle_id"]
        city_id = validated_data["city_id"]
        bundle = validated_data["bundle"]

        vehicle = Vehicle.objects.get(id=vehicle_id)
        city = City.objects.get(id=city_id)

        bundle.redeem_ticket()

        ticket = ParkingTicket.objects.create(
            user=user, vehicle=vehicle, city=city, minutes_issued=bundle.ticket_minutes
        )

        return ticket


class TicketBundleDetailSerializer(serializers.ModelSerializer):
    remaining_tickets = serializers.SerializerMethodField()

    class Meta:
        model = ParkingTicketBundle
        fields = [
            "id",
            "purchased_at",
            "quantity",
            "tickets_redeemed",
            "ticket_minutes",
            "price_paid",
            "remaining_tickets",
        ]

    def get_remaining_tickets(self, obj) -> int:
        return obj.remaining_tickets()
