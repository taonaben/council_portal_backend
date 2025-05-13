from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from portal.models import Vehicle, VehicleApproval
from django_redis import get_redis_connection
from portal.features.vehicles.vehicle_serializers import VehicleSerializer
import json


@receiver(post_save, sender=Vehicle)
def create_vehicle_review(sender, instance, created, **kwargs):
    """
    Automatically creates a VehicleApproval entry when a new Vehicle is added.
    """
    if created:
        VehicleApproval.objects.create(vehicle=instance, review_status="pending")
    # Invalidate and repopulate vehicle cache for user
    user_id = instance.owner.id
    redis = get_redis_connection("default")
    key = f"vehicles:{user_id}"
    vehicles = Vehicle.objects.filter(owner=instance.owner).order_by("-registered_at")[
        :10
    ]
    serializer = VehicleSerializer(vehicles, many=True)
    redis.set(key, json.dumps(serializer.data), ex=60 * 15)


@receiver(post_delete, sender=Vehicle)
def invalidate_vehicle_cache_on_delete(sender, instance, **kwargs):
    user_id = instance.owner.id
    redis = get_redis_connection("default")
    key = f"vehicles:{user_id}"
    vehicles = Vehicle.objects.filter(owner=instance.owner).order_by("-registered_at")[
        :10
    ]
    serializer = VehicleSerializer(vehicles, many=True)
    redis.set(key, json.dumps(serializer.data), ex=60 * 15)


@receiver(post_save, sender=VehicleApproval)
def approve_vehicle_review(sender, instance, created, **kwargs):
    """
    Updates the Vehicle's approval_status when a VehicleApproval is reviewed.
    """
    if not created and instance.vehicle.approval_status != instance.review_status:
        instance.vehicle.approval_status = instance.review_status
        instance.vehicle.save(update_fields=["approval_status"])
