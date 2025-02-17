from rest_framework import serializers
from portal.models import IssueReport


class IssueReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = IssueReport
        fields = (
            "id",
            "user",
            "city",
            "category",
            "description",
            "status",
            "created_at",
        )

        read_only_fields = ("id", "user", "city", "created_at")
