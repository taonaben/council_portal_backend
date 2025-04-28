from portal.models import Property
from portal.features.properties.properties_serializers import PropertySerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework import pagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class properties_list(generics.ListCreateAPIView):
    serializer_class = PropertySerializer
    pagination_class = pagination.PageNumberPagination
    # pagination_class.page_size = 10
    pagination_class.page_size_query_param = "page_size"
    max_page_size = 100

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()

    def get_queryset(self):
        if self.request.user.is_staff:
            return Property.objects.filter(city=self.request.user.city)
        else:
            return Property.objects.filter(owner=self.request.user)


class property_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    lookup_url_kwarg = "property_id"

    def get_permissions(self):
        if self.request.method == ["DELETE", "PUT", "PATCH"]:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()
