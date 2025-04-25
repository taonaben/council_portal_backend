from django.urls import path

from portal.features.water import water_views as views


urlpatterns = [
    path(
        "water_bill_list/",
        views.water_bill_list.as_view(),
        name="water_bill_list",
    ),
    path(
        "water_bill/<uuid:water_bill_id>/",
        views.water_bill_detail.as_view(),
        name="water_bill",
    ),
]
