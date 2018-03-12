import pytest
import uuid
from django.utils.timezone import now
from faker import Faker

fake = Faker()


@pytest.mark.django_db
class TestRecordViews:
    def test_should_return_error_with_invalid_data(self, client):
        response = client.post('/record/')
        assert response.status_code == 400

    def test_should_create_new_record(self, client):
        data = {
            'type': 'start',
            'call_id': uuid.uuid4(),
            'timestamp': now().isoformat(),
            'source': fake.msisdn(),
            'destination': fake.msisdn()
        }
        response = client.post('/record/', data)
        assert response.status_code == 201
