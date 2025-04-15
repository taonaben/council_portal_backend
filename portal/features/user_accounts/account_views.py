from urllib import request
from portal.models import Account
from portal.features.user_accounts.account_serializer import AccountSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from rest_framework.permissions import IsAuthenticated, IsAdminUser


class AccountView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(user__city=self.request.user.city)


class AccountDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    lookup_url_kwarg = "account_id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
