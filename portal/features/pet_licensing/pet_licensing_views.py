from portal.models import PetLicensing
from portal.features.pet_licensing.pet_licensing_serializers import PetLicenseSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

class pet_licensing_list(generics.ListCreateAPIView):
    serializer_class = PetLicenseSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return PetLicensing.objects.filter(user_id=user_id)
    
    def post(self, request, *args, **kwargs):
        serializer = PetLicenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class pet_licensing_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PetLicensing.objects.all()
    serializer_class = PetLicenseSerializer
    lookup_url_kwarg = 'license_id'
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        instance.delete()
