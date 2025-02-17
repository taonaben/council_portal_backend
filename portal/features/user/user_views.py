from portal.models import User
from portal.features.user.user_serializer import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics


class user_list(generics.ListCreateAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        # return User.objects.filter(city=self.request.user.city)  # filter by admin city
        return User.objects.all()


class user_detail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_url_kwarg = 'user_id'

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        instance.delete()