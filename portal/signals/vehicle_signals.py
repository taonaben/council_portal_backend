from django.db.models.signals import post_save
from django.dispatch import receiver
from portal.models import Vehicle, VehicleApproval

@receiver(post_save, sender=Vehicle)
def create_vehicle_review(sender, instance, created, **kwargs):
    """
    Automatically creates a VehicleApproval entry when a new Vehicle is added.
    """
    if created:
        VehicleApproval.objects.create(vehicle=instance, review_status="pending")


@receiver(post_save, sender=VehicleApproval)
def approve_vehicle_review(sender, instance, created, **kwargs):
    """
    Updates the Vehicle's approval_status when a VehicleApproval is reviewed.
    """
    if not created and instance.vehicle.approval_status != instance.review_status:
        instance.vehicle.approval_status = instance.review_status
        instance.vehicle.save(update_fields=["approval_status"])

