import django_filters
from portal.models import Vehicle, VehicleApproval


class VehicleReviewFilter(django_filters.FilterSet):
    class Meta:
        model = VehicleApproval
        fields = {
            "review_status": ["iexact"],
            "review_date": ["iexact", "gt", "lt"],
            "rejection_reason": ["icontains"],
        }

class VehicleFilter(django_filters.FilterSet):
    class Meta:
        model = Vehicle
        fields = {
            "plate_number": ["iexact"],
            "brand": ["iexact", 'icontains'],
            "model": ["iexact", 'icontains'],
            "color": ["iexact", 'icontains'],
            "approval_status": ["iexact"],
            "registered_at": ["iexact", "gt", "lt"],
        }
