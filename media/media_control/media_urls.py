from django.urls import path
from . import medial_views

urlpatterns = [
    path('media/<path:path>/', medial_views.media_view, name='media_view'),
]