from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db import transaction
from portal.models import Property, Account
import logging


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Property)
def create_account_for_property(sender, instance, created, **kwargs):
    """
    Automatically creates a User Account entry when a new Property is added.
    """
    if created and instance.owner:
        try:
            with transaction.atomic():
                # Create account with generated account number
                if not Account.objects.filter(property=instance).exists():
                    account = Account.objects.create(
                        user=instance.owner,
                        property=instance,
                    )

                    account.save()

                # Prepare context for email template
                context = {
                    "property_address": instance.address,
                    "account_number": account.account_number,
                    "water_meter_number": account.water_meter_number,
                }

                # # Render HTML email
                # html_message = render_to_string(
                #     "emails/new_account_created.html", context
                # )

                # Send email notification
                send_mail(
                    subject="Welcome to City Council Portal - New Account Created",
                    message=f"""A new property account has been created.
                    Property Address: {instance.address}
                    Account Number: {account.account_number}
                    Water Meter Number: {account.water_meter_number}""",
                    from_email="no-reply@example.com",
                    recipient_list=[instance.owner.email],
                    # html_message=html_message,
                    fail_silently=True,
                )
                logger.info(f"Account created for property: {instance.address}")
        except Exception as e:
            # Log the error but don't prevent property creation
            logger.error(f"Error creating account for property: {str(e)}")
    else:
        logger.warning(
            f"No owner associated with property {instance.id}. Account not created."
        )
