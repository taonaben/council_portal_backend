from urllib import request
from portal.models import Account
from portal.features.user_accounts.account_serializer import AccountSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django_redis import get_redis_connection
import json
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.core.cache import cache

from rest_framework.permissions import IsAuthenticated, IsAdminUser


def _convert_uuids_to_str(data):
    if isinstance(data, dict):
        return {k: _convert_uuids_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_convert_uuids_to_str(i) for i in data]
    elif hasattr(data, "hex") and hasattr(data, "int"):
        return str(data)
    return data


class AccountView(generics.ListCreateAPIView):
    serializer_class = AccountSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Account.objects.all(property__city=user.city)
        return Account.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = request.user
        cache.delete(f"accounts:{user.id}")
        return response

    @method_decorator(cache_control(private=True, max_age=60 * 15))
    def list(self, request, *args, **kwargs):
        user = request.user
        cache_key = f"accounts:{user.id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(json.loads(cached_data))

        queryset = self.get_queryset().order_by("-created_at")[:10]
        serializer = self.get_serializer(queryset, many=True)
        data = _convert_uuids_to_str(serializer.data)

        cache.set(cache_key, json.dumps(data), timeout=60 * 15)
        return Response(data)


class AccountDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    lookup_url_kwarg = "account_number"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
