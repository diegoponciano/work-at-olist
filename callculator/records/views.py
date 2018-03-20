from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from rest_framework import generics

from .models import CallRecord
from .serializers import RecordSerializer, BillSerializer


class CallDetails(generics.RetrieveAPIView):
    serializer_class = RecordSerializer
    queryset = CallRecord.objects.all()
    lookup_field = 'call_id'


class RecordCall(generics.CreateAPIView):
    serializer_class = RecordSerializer


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
