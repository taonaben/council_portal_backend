from django.urls import path
import portal.features.properties.properties_views as views

urlpatterns = [
    path('', views.properties_list.as_view(), name='properties'),
    path('<uuid:property_id>/', views.property_detail.as_view(), name='property-detail'),
]