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

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        return attrs