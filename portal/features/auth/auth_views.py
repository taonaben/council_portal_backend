from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, logout, login
from portal.features.auth.send_code import send_verification_code_via_email
from portal.models import User, VerificationCode
from portal.features.auth.auth_serializer import (
    VerificationCodeSerializer,
    LoginSerializer,
    LogoutSerializer,
    ResendCodeSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from rest_framework import generics
from rest_framework import status
from .auth_serializer import RegistrationSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create user with validated data
        user = User.objects.create_user(
            username=serializer.validated_data["username"],
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
            phone_number=serializer.validated_data["phone_number"],
            city=serializer.validated_data["city"],
            is_active=False,  # User starts inactive until verified
        )

        # Send verification code
        send_verification_code_via_email(user)

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": user.id,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": "Registration successful. Please check your email for verification.",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        # Use a generic error message for security
        error_msg = "Invalid credentials or inactive account"

        try:
            user = authenticate(request, username=username, password=password)

            if user is None:
                return Response({"error": error_msg}, status=401)

            if not user.is_active:
                return Response({"error": error_msg}, status=401)

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user": user.id,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "message": "Login successful",
                },
                status=200,
            )

        except Exception:
            return Response({"error": error_msg}, status=401)


class ResendCode(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResendCodeSerializer

    def post(self, request):
        username = request.data.get("username")
        user = User.objects.get(username=username)
        send_verification_code_via_email(user)
        return Response({"message": "Verification code sent"})


class VerifyCodeView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerificationCodeSerializer

    def post(self, request):
        username = request.data.get("username")
        code = request.data.get("code")

        try:
            user = User.objects.get(username=username)
            verification = VerificationCode.objects.filter(user=user, code=code).first()

            if not verification:
                return Response({"error": "Invalid code"}, status=400)
            if verification.is_expired():
                return Response({"error": "Code expired"}, status=400)

            # Delete code after successful verification
            verification.delete()

            # Activate user
            user.is_active = True
            user.save()

            return Response(
                {"success": f"user {username} verified successfully"}, status=201
            )
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=400)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required."}, status=400)

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logout successful, token invalidated."}, status=200
            )
        except Exception as e:
            return Response({"error": str(e)}, status=400)
