from django.utils import timezone
from datetime import timedelta, datetime, date
from django.db.models.signals import post_save

from django.dispatch import receiver
from portal.models import BusinessLicense, Business, BusinessLicenseApproval

@receiver(post_save, sender=BusinessLicense)
def update_license_status(instance, **kwargs):
    now = timezone.now()

    if instance.status == "active" and instance.expiration_date and instance.expiration_date <= now:
        instance.status = 'expired'
        instance.save(update_fields=['status'])



@receiver(post_save, sender=BusinessLicense)
def create_license_review(sender, instance, created, **kwargs):
    if created:
        BusinessLicenseApproval.objects.create(license=instance, review_status = "pending")

@receiver(post_save, sender=BusinessLicenseApproval)
def approve_business_license(sender, instance, created, **kwargs):
    if not created and instance.license.approval_status != instance.review_status:
        instance.license.approval_status = instance.review_status
        instance.license.save(update_fields=["approval_status"])
