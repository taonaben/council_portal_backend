from django.urls import path
from portal.features.user import user_views as views

urlpatterns = [
    path('all/', views.user_list.as_view(), name='user_list'),
    path('<int:user_id>/', views.user_detail.as_view(), name='user_detail'),
]