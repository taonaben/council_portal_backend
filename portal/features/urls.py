from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from portal.features.properties.properties_urls import urlpatterns as property_urls
from portal.features.city.city_urls import urlpatterns as city_urls
from portal.features.announcements.announcements_urls import (
    urlpatterns as announcement_urls,
)
from portal.features.business.business_urls import urlpatterns as business_urls
from portal.features.issues.issues_urls import urlpatterns as issue_urls
from portal.features.parking.parking_urls import urlpatterns as parking_urls
from portal.features.pet_licensing.pet_licensing_urls import (
    urlpatterns as pet_licensing_urls,
)
from portal.features.taxes.tax_urls import urlpatterns as tax_urls
from portal.features.users.user_urls import urlpatterns as user_urls
from portal.features.vehicles.vehicle_urls import urlpatterns as vehicle_urls
from portal.features.water.water_urls import urlpatterns as water_urls
from media.media_control.media_urls import urlpatterns as media_urls
from portal.features.auth.auth_urls import urlpatterns as auth_urls
from portal.features.user_accounts.account_urls import urlpatterns as account_urls


urlpatterns = [
    path("announcements/", include(announcement_urls)),
    path("auth/", include(auth_urls)),
    path("cities/", include(city_urls)),
    path("business/", include(business_urls)),
    path("issues/", include(issue_urls)),
    path("parking_tickets/", include(parking_urls)),
    path("pet_licensing/", include(pet_licensing_urls)),
    path("properties/", include(property_urls)),
    path("taxes/", include(tax_urls)),
    path("users/", include(user_urls)),
    path("accounts/", include(account_urls)),
    path("vehicles/", include(vehicle_urls)),
    path("water/", include(water_urls)),
    path("", include(media_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
