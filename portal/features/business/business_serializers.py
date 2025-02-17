from rest_framework import serializers
from portal.models import Business, BusinessLicense, BusinessLicenseApproval


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = (
            "id",
            "owner",
            "city_registered",
            "name",
            "type",
            "purpose",
            "reg_num",
            "licenses",
            "tax",
            "address",
            "status",
        )

        read_only_fields = (
            "id",
            "owner",
            "city_registered",
            "reg_num",
            "status",
            "licenses",
        )


class BusinessLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessLicense
        fields = (
            "id",
            "business",
            "type",
            "issue_date",
            "duration_months",
            "expiration_date",
            "license_fee",
            "approval_status",
            "status",
        )

        read_only_fields = (
            "id",
            "issue_date",
            "expiration_date",
            "license_fee",
            "status",
            "approval_status",
        )


class BusinessLicenseApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessLicenseApproval
        fields = (
            "id",
            "license",
            "admin",
            "review_status",
            "review_date",
            "rejection_reason",
        )

        read_only_fields = (
            "id",
            "license",
            "admin",
            "review_date",
        )
