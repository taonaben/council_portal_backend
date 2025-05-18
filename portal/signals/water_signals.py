import random
from datetime import datetime, timedelta
from django.db.models.signals import post_save, post_delete
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from portal.models import WaterUsage, WaterBill
from django_redis import get_redis_connection
from portal.features.water.water_serializers import WaterBillSerializer
import json


# @receiver(post_save, sender=WaterUsage)
# def update_water_meter(instance, **kwargs):
#     """Update the water meter reading when a new water usage entry is added."""
#     instance.meter.current_reading += instance.consumption
#     instance.meter.save()


# # @receiver(post_save, sender=WaterMeter)
# def generate_daily_water_usage():
#     """Function to simulate daily water usage."""
#     now = timezone.now()
#     meters = WaterMeter.objects.all()

#     for meter in meters:
#         daily_usage = round(random.uniform(50, 300), 2)  # Random daily usage in liters
#         WaterUsage.objects.create(
#             meter=meter,
#             property=meter.property,
#             consumption=daily_usage,
#             date_recorded=now,
#         )
#         meter.current_reading += daily_usage
#         meter.save()


# # @receiver(post_save, sender=WaterMeter)
# def generate_monthly_water_bills():
#     """Generate monthly water bills based on usage."""
#     today = timezone.now().date()
#     first_day_of_month = today.replace(day=1)

#     # Get all properties and calculate total usage for the month
#     meters = WaterMeter.objects.all()
#     for meter in meters:
#         monthly_usage = (
#             WaterUsage.objects.filter(
#                 meter=meter, date_recorded__gte=first_day_of_month
#             ).aggregate(total_usage=models.Sum("consumption"))["total_usage"]
#             or 0
#         )

#         # Set price per unit of water
#         price_per_liter = 0.005  # Example: 0.005 per liter
#         total_amount = monthly_usage * price_per_liter

#         # Create the bill
#         WaterBill.objects.create(
#             property=meter.property,
#             water_used=monthly_usage,
#             meter_number=meter.meter_num,
#             amount_owed=total_amount,
#         )


# @receiver(post_save, sender=WaterBill)
def change_water_bill_status():
    """Change the status of the water bill."""
    bill = WaterBill.objects.get(id=1)
    if bill.amount_paid >= bill.amount_owed:
        bill.status = "paid"

    bill.save()


# @receiver([post_save, post_delete], sender=WaterBill)
# def invalidate_water_bill_cache(sender, instance, **kwargs):
#     user_id = instance.user.id
#     redis = get_redis_connection("default")
#     key = f"water_bills:{user_id}"
#     bills = WaterBill.objects.filter(user=instance.user).order_by("-created_at")[:10]
#     serializer = WaterBillSerializer(bills, many=True)
#     redis.set(key, json.dumps(serializer.data), ex=60 * 15)
