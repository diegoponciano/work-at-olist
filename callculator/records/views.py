from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import CallRecord
from .serializers import get_record_serializer, RecordSerializer


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


class Bills(generics.GenericAPIView):
    def get(self, request, phone, month_year=None, format=None):
        if month_year:
            month, year = map(int, month_year.split('-'))
        else:
            previous = now() - relativedelta(months=1)
            month, year = previous.month, previous.year
        records = CallRecord.objects.filter(
            started_at__year=year,
            started_at__month=month,
            source=phone)
        serializer = RecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
