from rest_framework import serializers
from portal.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'city',
        )

        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }
        