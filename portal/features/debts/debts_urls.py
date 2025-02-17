from django.urls import path
import portal.features.debts.debts_views as views

urlpatterns = [
    path('all/<uuid:user_id>', views.debt_list.as_view(), name='debt_list'),
    path('detail/<uuid:pk>/', views.debt_detail.as_view(), name='debt_detail'),
]