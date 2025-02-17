from rest_framework import serializers
from portal.models import Vehicle, VehicleApproval


class VehicleSerializer(serializers.ModelSerializer):

    ticket_count = serializers.SerializerMethodField(method_name="get_ticket_count")

    def get_ticket_count(self, obj):
        count = int(obj.parking_tickets.count())
        return count

    class Meta:
        model = Vehicle
        fields = (
            "id",
            "owner",
            "plate_number",
            "brand",
            "model",
            "color",
            "tax",
            "parking_tickets",
            "ticket_count",
            "approval_status",
            "city_registered",
            "registered_at",
        )

        read_only_fields = (
            "id",
            "ticket_count",
            "parking_tickets",
            "registered_at",
            "approval_status",
            'city_registered',
            'owner',
        )

        extra_kwargs = {
            "plate_number": {"required": True},
            "brand": {"required": True},
            "model": {"required": True},
            "color": {"required": True},
            "tax": {"required": True},
            "owner": {"required": True},
        }


class VehicleApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleApproval
        fields = (
            "id",
            "vehicle",
            "admin",
            "review_status",
            "review_date",
            "rejection_reason",
        )

        read_only_fields = (
            "id",
            "admin",
            "review_date",
        )

        extra_kwargs = {
            "review_status": {"required": True},
            "rejection_reason": {"required": False},
        }

