import pytest
import uuid
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
        record = CallRecord(started_at=start, ended_at=end,
                            call_id=uuid.uuid4())
        record.save()

        assert record.duration == timedelta(minutes=30)


@pytest.mark.django_db
class TestStardardMinutesCalculation:
    def test_standard_minutes_at_same_day(self):
        start = parse('01-01-2018 21:57:13Z')
        end = parse('01-01-2018 22:10:56Z')
        record = CallRecord(started_at=start, ended_at=end,
                            call_id=uuid.uuid4())

        assert record.standard_minutes() == 2

        record.started_at = parse('01-01-2018 21:00:00Z')
        assert record.standard_minutes() == 60

    def test_standard_minutes_on_two_days(self):
        start = parse('01-01-2018 21:57:13Z')
        end = parse('01-02-2018 6:10:56Z')
        record = CallRecord(started_at=start, ended_at=end,
                            call_id=uuid.uuid4())

        assert record.standard_minutes() == 12


@pytest.mark.django_db
class TestPricingRules:
    def test_reduced_tariff_charges_only_standing_charge(self):
        start = parse('01-01-2018 22:57:13Z')
        end = parse('01-01-2018 23:10:56Z')
        record = CallRecord(started_at=start, ended_at=end,
                            call_id=uuid.uuid4())
        record.save()

        assert record.price == 0.36

    def test_standard_call_charges_standing_and_minutely(self):
        start = parse('01-01-2018 20:55:13Z')
        end = parse('01-01-2018 20:58:56Z')
        record = CallRecord(started_at=start, ended_at=end,
                            call_id=uuid.uuid4())
        record.save()

        assert record.price == 0.36 + 0.09*3

    def test_mixed_standard_and_reduced_tariff(self):
        start = parse('01-01-2018 21:57:13Z')
        end = parse('01-01-2018 22:10:56Z')
        record = CallRecord(started_at=start, ended_at=end,
                            call_id=uuid.uuid4())
        record.save()

        assert record.price == 0.36 + 0.09*2
