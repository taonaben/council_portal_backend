from rest_framework import serializers

from portal.models import Property

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            'id',
            'owner',
            'city',
            'community',
            'area_sq_m',
            'address',
            'value',
            'property_type',
            'housing_status',
            'tax'
            
        )

        read_only_fields = ('id', )
        extra_kwargs = {
            'owner': {'write_only': True},
        }

    def validate_area_sq_m(self, value):
        if value < 0:
            raise serializers.ValidationError("Area must be greater than 0")
        return value
    
    def validate_value(self, value):
        if value < 0:
            raise serializers.ValidationError("Value must be greater than 0")
        return value