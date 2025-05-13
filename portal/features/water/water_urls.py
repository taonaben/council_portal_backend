from django.urls import path
from portal.features.water import water_views as views

urlpatterns = [
    path(
        "add_water_bill/",
        views.CreateWaterBillView.as_view(),
        name="create_water_bill",
    ),
    path(
        "water_bill_list/",
        views.WaterBillListAll.as_view(),
        name="water_bill_list",
    ),
    path(
        "water_bill_list_by_account/<int:account_id>/",
        views.WaterBillListByAccount.as_view(),
        name="water_bill_list_all",
    ),
    path(
        "water_bill/<uuid:water_bill_id>/",
        views.water_bill_detail.as_view(),
        name="water_bill",
    ),
    path(
        "latest_water_bill/<int:account_id>/",
        views.LatestWaterBillView.as_view(),
        name="latest_water_bill",
    ),
]
