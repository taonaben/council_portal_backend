from django.db.models.signals import post_save
from django.dispatch import receiver
from portal.features.auth.send_code import send_verification_code_via_email
from portal.models import User


@receiver(post_save, sender=User)
def send_verification_code_on_user_creation(sender, instance, created, **kwargs):
    if created:
        send_verification_code_via_email(instance)
