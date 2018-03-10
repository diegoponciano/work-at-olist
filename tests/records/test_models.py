import pytest

from callculator.records.models import CallRecord


@pytest.mark.django_db
class TestRecord:
    def test_record_creation(self):
        record = CallRecord()
        record.save()
        assert record.id
