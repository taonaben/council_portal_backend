from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from portal.models import ParkingTicket
from django_redis import get_redis_connection
from portal.features.parking.parking_serializers import ParkingTicketSerializer
import json


@receiver(post_save, sender=ParkingTicket)
def update_ticket_status(sender, instance, created, **kwargs):
    now = timezone.now()  # Ensure timezone-aware datetime
    if instance.status == "active" and instance.expiry_at <= now:  # Fix comparison
        instance.status = "expired"
        instance.save(update_fields=["status"])



