from os import read
from portal.models import VerificationCode, User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = (
            "user",
            "code",
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)

    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if not username or not password:
            raise serializers.ValidationError("Must provide username and password")

        return attrs


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "phone_number",
            "city",
        )
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "phone_number": {"required": True},
            "city": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        # Validate unique email and phone
        email = attrs.get("email")
        username = attrs.get("username")

        phone = attrs.get("phone_number")
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already registered"})
        
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username already exists"})
        
        if User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError(
                {"phone_number": "Phone number already registered"}
            )

        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ResendCodeSerializer(serializers.Serializer):
    username = serializers.CharField()
