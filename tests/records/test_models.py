import pytest
from dateutil.parser import parse
from datetime import timedelta

from callculator.records.models import CallRecord


@pytest.mark.django_db
class TestRecord:
    def test_record_creation(self):
        record = CallRecord()
        record.save()

        assert record.id

    def test_calculates_duration(self):
        start = parse('01-01-2018 16:00Z')
        end = parse('01-01-2018 16:30Z')
        record = CallRecord(started_at=start, ended_at=end)
        record.save()

        assert record.duration == timedelta(minutes=30)
