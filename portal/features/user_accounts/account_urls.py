from django.urls import path

from portal.features.user_accounts import account_views as views

urlpatterns = [
    path('all/', views.AccountView.as_view(), name='account_list'),
    path('<int:account_number>/', views.AccountDetail.as_view(), name='account_detail'),
]