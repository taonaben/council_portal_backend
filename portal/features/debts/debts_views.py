from portal.models import Debt
from portal.features.debts.debts_serializers import DebtSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

class debt_list(generics.ListCreateAPIView):
    serializer_class = DebtSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Debt.objects.filter(user_id=user_id)
    
    def post(self, request, *args, **kwargs):
        serializer = DebtSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class debt_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer
    lookup_url_kwarg = 'pk'
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        instance.delete()