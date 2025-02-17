from django.urls import path
import portal.features.pet_licensing.pet_licensing_views as views

urlpatterns = [
    path('<int:user_id>/all/', views.pet_licensing_list.as_view(), name='pet_licensing_list'),
    path('<int:user_id>/<uuid:license_id>/', views.pet_licensing_detail.as_view(), name='pet_licensing_detail'),
    
]