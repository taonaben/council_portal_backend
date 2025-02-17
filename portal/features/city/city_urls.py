from django.urls import path
import portal.features.city.city_views as views

urlpatterns = [
    path('all/', views.cities_list.as_view(), name='cities'),
    path('<uuid:pk>/', views.city_detail.as_view(), name='city-detail'),
    path('<uuid:city_id>/sections/', views.city_sections_list.as_view(), name='city-sections'),
    path('sections/<uuid:pk>/', views.city_section_detail.as_view(), name='city-section-detail'),
]