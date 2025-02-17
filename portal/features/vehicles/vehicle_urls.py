from django.urls import path
import portal.features.vehicles.vehicle_views as views

urlpatterns = [
    path("all/", views.VehicleList.as_view(), name="vehicle_list"),
    path("<uuid:vehicle_id>/", views.VehicleDetail.as_view(), name="vehicle_detail"),
    path("reviews/", views.VehicleReviewList.as_view(), name="vehicle_review_list"),
    path(
        "reviews/<uuid:vehicle_review_id>/",
        views.VehicleReviewDetail.as_view(),
        name="vehicle_review_detail",
    ),
]
