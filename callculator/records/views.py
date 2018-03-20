from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import CallRecord
from .serializers import get_record_serializer
from .serializers import RecordSerializer, BillSerializer


class CallDetails(generics.GenericAPIView):
    def get(self, request, pk, format=None):
        try:
            instance = CallRecord.objects.get(call_id=pk)
            serializer = RecordSerializer(instance=instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CallRecord.DoesNotExist:
            raise NotFound


class RecordCall(generics.GenericAPIView):
    def get_serializer_class(self):
        return get_record_serializer(self.request.data)

    def post(self, request, format=None):
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Bills(generics.ListAPIView):
    serializer_class = BillSerializer

    def get_queryset(self):
        if 'month_year' in self.kwargs:
            month, year = map(int, self.kwargs['month_year'].split('-'))
        else:
            previous = now() - relativedelta(months=1)
            month, year = previous.month, previous.year
        return CallRecord.objects.filter(
            started_at__year=year,
            started_at__month=month,
            source=self.kwargs['phone']).order_by('started_at')
