from django.urls import path
from portal.features.auth import auth_views as views

urlpatterns = [
    path('resend_code/', views.ResendCode.as_view(), name='resend_code'),
    path('verify/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
