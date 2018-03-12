from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import get_record_serializer


class RecordCall(generics.GenericAPIView):
    def get_serializer_class(self):
        return get_record_serializer(self.request.data)

    def post(self, request, format=None):
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            # serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
