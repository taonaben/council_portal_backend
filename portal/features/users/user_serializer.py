from functools import partial
from rest_framework import serializers
from portal.features.user_accounts.account_serializer import AccountSerializer
from portal.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "accounts",
            "email",
            "phone_number",
            "password",
            "properties",
            "city",
            "is_staff",
            "is_superuser",
            "is_active",
        )

        read_only_fields = (
            "id",
            "is_staff",
            "is_superuser",
            "accounts",
            "is_active",
            "properties",
        )

        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data["phone_number"],
            city=validated_data["city"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.username = validated_data.get("username", instance.username)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.city = validated_data.get("city", instance.city)

        password = validated_data.get("password", None)
        if password:
            instance.set_password(password)

        
        instance.save()
        return instance
