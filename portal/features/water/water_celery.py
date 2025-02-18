from celery import shared_task
from portal.signals.water_signals import generate_daily_water_usage, generate_monthly_water_bills

@shared_task
def daily_water_usage_task():
    generate_daily_water_usage()

@shared_task
def monthly_water_bill_task():
    generate_monthly_water_bills()
