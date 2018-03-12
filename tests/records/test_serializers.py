import pytest
import uuid
from django.utils.timezone import now
from faker import Faker

from callculator.records.serializers import get_record_serializer

fake = Faker()


@pytest.mark.django_db
class TestRecordSerializer:
    def test_start_call_requires_phones(self):
        data = {
            'type': 'start',
            'call_id': str(uuid.uuid4())
        }
        serializer = get_record_serializer(data)(data=data)

        assert not serializer.is_valid()

        data = {
            'type': 'start',
            'call_id': str(uuid.uuid4()),
            'timestamp': now().isoformat(),
            'source': fake.msisdn(),
            'destination': fake.msisdn()
        }
        serializer = get_record_serializer(data)(data=data)

        assert serializer.is_valid()

    def test_end_call_does_not_require_phones(self):
        data = {
            'type': 'end',
            'call_id': str(uuid.uuid4()),
            'timestamp': now().isoformat(),
        }
        serializer = get_record_serializer(data)(data=data)

        assert serializer.is_valid()
