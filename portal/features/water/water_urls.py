from django.urls import path
from rest_framework.routers import DefaultRouter

from portal.features.water import water_views as views

router = DefaultRouter()
router.register('water_bills', views.WaterBillView, basename='water_bills')
router.register('water_meters', views.WaterMeterView, basename='water_meters')
router.register('water_usages', views.WaterUsageView, basename='water_usages')

urlpatterns = router.urls