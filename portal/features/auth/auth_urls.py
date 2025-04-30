from django.urls import path
from portal.features.auth import auth_views as views

urlpatterns = [
    path("resend_code/", views.ResendCode.as_view(), name="resend_code"),
    path("verify/", views.VerifyCodeView.as_view(), name="verify_code"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
