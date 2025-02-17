from django.db.models.signals import pre_save
from django.dispatch import receiver
from portal.models import WaterMeter, WaterUsage
from django.utils import timezone

@receiver(pre_save, sender=WaterMeter)
def record_water_usage(sender, instance, **kwargs):
    if instance.pk:
        previous_reading = WaterMeter.objects.get(pk=instance.pk).current_reading
        if instance.current_reading != previous_reading:
            WaterUsage.objects.create(
                meter=instance,
                property=instance.property,
                consumption=instance.current_reading - previous_reading,
                date_recorded=timezone.now()
            )