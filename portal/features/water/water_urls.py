from django.urls import path

from portal.features.water import water_views as views


urlpatterns = [
    path(
        "water_meter_list/",
        views.water_meter_list.as_view(),
        name="water meter list",
    ),
    path(
        "water_meter/<uuid:meter_id>/",
        views.water_meter_detail.as_view(),
        name="water meter detail",
    ),
    path(
        "water_usage/",
        views.water_usage_list.as_view(),
        name="water usage list",
    ),
    path(
        "water_usage/<uuid:usage_id>/",
        views.water_usage_detail.as_view(),
        name="water usage detail",
    ),
    path(
        "water_bill_list/",
        views.water_bill_list.as_view(),
        name="water bill list",
    ),
    path(
        "water_bill/<uuid:water_bill_id>/",
        views.water_bill_detail.as_view(),
        name="water bill",
    ),
    path(
        "total_water_debt/",
        views.total_water_debt.as_view(),
        name="total water debt",
    ),
]
