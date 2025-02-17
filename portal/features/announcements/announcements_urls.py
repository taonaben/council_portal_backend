from django.urls import path
import portal.features.announcements.announcements_views as views

urlpatterns = [
    path("all/", views.announcements_list.as_view(), name="announcements_list"),
    path(
        "<uuid:announcement_id>/",
        views.announcement_detail.as_view(),
        name="announcement_detail",
    ),
    path(
        "<uuid:announcement_id>/comments/",
        views.announcement_comments_list.as_view(),
        name="announcement_comments_list",
    ),
    path(
        "comments/<uuid:announcement_comment_id>/",
        views.announcement_comment_detail.as_view(),
        name="announcement_comment_detail",
    ),
]
