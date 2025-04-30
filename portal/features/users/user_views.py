from portal.models import User
from portal.features.users.user_serializer import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny


class user_list(generics.ListCreateAPIView):
    serializer_class = UserSerializer
 
    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.filter(city=self.request.user.city)
        else:
            return User.objects.filter(id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(is_active=False)


class user_detail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_url_kwarg = 'user_id'
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)