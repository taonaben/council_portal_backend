from django.urls import path
import portal.features.parking.parking_views as views

urlpatterns = [
    path("all/", views.ParkingList.as_view(), name="parking_list"),
    # path("summary/", views.ParkingSummary.as_view(), name="parking_summary"),
    # path(
    #     "weekly-income/",
    #     views.WeeklyIncomeParkingSummary.as_view(),
    #     name="weekly-income",
    # ),
    path(
        "ticket-bundles/purchase/",
        views.TicketBundlePurchaseView.as_view(),
        name="purchase-ticket-bundle",
    ),
    path(
        "ticket-bundles/redeem/", views.RedeemTicketView.as_view(), name="redeem-ticket"
    ),
    path(
        "ticket-bundles/",
        views.TicketBundleListView.as_view(),
        name="list-ticket-bundles",
    ),
    path("<uuid:ticket_id>/", views.ParkingDetail.as_view(), name="parking_detail"),
    path(
        "active-ticket/",
        views.ActiveParkingTicketsView.as_view(),
        name="active-parking-tickets",
    ),
    path(
        "vehicle/<str:vehicle_id>/",
        views.VehicleParkingTicketList.as_view(),
        name="parking_list_by_vehicle",
    ),
]
