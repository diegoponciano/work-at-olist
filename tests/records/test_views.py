import pytest
import uuid
from dateutil.parser import parse
from faker import Faker

fake = Faker()


def fake_phonenumber():
    return fake.numerify(fake.random_element(('###########',)))


@pytest.mark.django_db
class TestRecordViews:
    start = {
        'type': 'start',
        'call_id': uuid.uuid4(),
        'timestamp': parse('01-01-2018 16:00Z').isoformat(),
        'source': fake_phonenumber(),
        'destination': fake_phonenumber()
    }
    end = {
        'type': 'end',
        'call_id': uuid.uuid4(),
        'timestamp': parse('01-01-2018 16:30Z').isoformat()
    }

    def test_should_return_error_with_invalid_data(self, client):
        response = client.post('/record/')
        assert response.status_code == 400

    def test_should_create_new_record(self, client):
        response = client.post('/record/', self.start)
        assert response.status_code == 201

    def test_should_set_start_datetime(self, client):
        response = client.post('/record/', self.start)
        assert parse(
            response.data['started_at']) == parse(self.start['timestamp'])

    def test_should_set_end_datetime(self, client):
        response = client.post('/record/', self.end)
        assert parse(
            response.data['ended_at']) == parse(self.end['timestamp'])

    def test_should_retrieve_call_record(self, client):
        self.start['call_id'] = self.end['call_id'] = uuid.uuid4()

        client.post('/record/', self.start)
        client.post('/record/', self.end)
        response = client.get('/record/%s/' % self.start['call_id'])

        assert response.status_code == 200
        assert parse(
            response.data['started_at']) == parse(self.start['timestamp'])
        assert parse(
            response.data['ended_at']) == parse(self.end['timestamp'])

    def test_should_calculate_duration(self, client):
        self.start['call_id'] = self.end['call_id'] = uuid.uuid4()

        client.post('/record/', self.start)
        response = client.post('/record/', self.end)

        assert response.data['duration'] == '00:30:00'

    def test_should_calculate_standard_price(self, client):
        self.start['call_id'] = self.end['call_id'] = uuid.uuid4()

        client.post('/record/', self.start)
        response = client.post('/record/', self.end)

        assert response.data['price'] == str(round(0.36 + 0.09*30, 2))

    def test_should_calculate_example_price(self, client):
        self.start['call_id'] = self.end['call_id'] = uuid.uuid4()
        self.start['timestamp'] = parse('01-01-2018 21:57:13Z').isoformat()
        self.end['timestamp'] = parse('01-01-2018 22:10:56Z').isoformat()

        client.post('/record/', self.start)
        response = client.post('/record/', self.end)

        assert response.data['price'] == '0.54'

    def test_should_calculate_reduced_price(self, client):
        self.start['call_id'] = self.end['call_id'] = uuid.uuid4()
        self.start['timestamp'] = parse('01-01-2018 22:07:13Z').isoformat()
        self.end['timestamp'] = parse('01-01-2018 22:40:56Z').isoformat()

        client.post('/record/', self.start)
        response = client.post('/record/', self.end)

        assert response.data['price'] == '0.36'
