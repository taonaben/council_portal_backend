from os import read
from portal.models import VerificationCode

from rest_framework import serializers


class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = (
            "user",
            "code",
        )
        read_only_fields = ("user",)




class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ResendCodeSerializer(serializers.Serializer):
    username = serializers.CharField()
