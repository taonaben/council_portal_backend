from django.urls import path
import portal.features.parking.parking_views as views

urlpatterns = [
    path("all/", views.ParkingList.as_view(), name="parking_list"),
    path("summary/", views.ParkingSummary.as_view(), name="parking_summary"),
    path("<uuid:ticket_id>/", views.ParkingDetail.as_view(), name="parking_detail"),
]
