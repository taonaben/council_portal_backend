from django.urls import path

from portal.features.business import business_views as views

urlpatterns = [
    path("all/", views.business_list.as_view(), name="business_list"),
    path(
        "<uuid:business_id>/", views.business_detail.as_view(), name="business_detail"
    ),
    path(
        "license/<uuid:business_id>/",
        views.business_license_list.as_view(),
        name="business_license_list",
    ),
    path(
        "license/<uuid:business_license_id>/",
        views.business_license_detail.as_view(),
        name="business_license_detail",
    ),
    path(
        "license_approvals/",
        views.business_license_approval_list.as_view(),
        name="business_license_approval_list",
    ),
    path(
        "license_approvals/<uuid:business_license_approval_id>/",
        views.business_license_approval_detail.as_view(),
        name="business_license_approval_detail",
    ),
]
