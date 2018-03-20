import pytest
import uuid
from django.utils.timezone import now
from faker import Faker

from callculator.records.serializers import RecordSerializer

fake = Faker()


@pytest.mark.django_db
class TestRecordSerializer:
    def test_start_call_requires_phones(self):
        data = {
            'type': 'start',
            'call_id': str(uuid.uuid4())
        }
        serializer = RecordSerializer(data=data)

        assert not serializer.is_valid()

        data = {
            'type': 'start',
            'call_id': str(uuid.uuid4()),
            'timestamp': now().isoformat(),
            'source': fake.msisdn(),
            'destination': fake.msisdn()
        }
        serializer = RecordSerializer(data=data)

        assert serializer.is_valid()

    def test_end_call_does_not_require_phones(self):
        data = {
            'type': 'end',
            'timestamp': now().isoformat(),
        }
        serializer = RecordSerializer(data=data)

        assert not serializer.is_valid()

        data = {
            'type': 'end',
            'call_id': str(uuid.uuid4()),
            'timestamp': now().isoformat(),
        }
        serializer = RecordSerializer(data=data)

        assert serializer.is_valid()

    def test_invalid_call_type(self):
        data = {
            'type': 'invalid',
            'call_id': str(uuid.uuid4()),
            'timestamp': now().isoformat(),
        }
        serializer = RecordSerializer(data=data)

        assert not serializer.is_valid()
