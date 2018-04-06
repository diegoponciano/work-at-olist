import decimal
import pytest
import pytz
import random
import uuid
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta as delta
from django.utils.timezone import now
from faker import Faker

from callculator.records.models import CallRecord

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
        response = client.post('/records/')
        assert response.status_code == 400

    def test_should_create_new_record(self, client):
        response = client.post('/records/', self.start)
        assert response.status_code == 201

    def test_should_set_start_datetime(self, client):
        response = client.post('/records/', self.start)
        assert parse(
            response.data['started_at']) == parse(self.start['timestamp'])

    def test_should_set_end_datetime(self, client):
        response = client.post('/records/', self.end)

        assert parse(
            response.data['ended_at']) == parse(self.end['timestamp'])

    def test_should_finish_only_one_call_record(self, client):
        records_before = CallRecord.objects.count()
        self.start['call_id'] = self.end['call_id'] = uuid.uuid4()

        response = client.post('/records/', self.start)
        assert response.status_code == 201

        response = client.post('/records/', self.end)
        assert response.status_code == 201
        assert parse(
            response.data['started_at']) == parse(self.start['timestamp'])
        assert parse(
            response.data['ended_at']) == parse(self.end['timestamp'])
        assert records_before + 1 == CallRecord.objects.count()

    def test_should_retrieve_call_record(self, client):
        self.start['call_id'] = self.end['call_id'] = uuid.uuid4()

        client.post('/records/', self.start)
        client.post('/records/', self.end)
        response = client.get('/records/%s/' % self.start['call_id'])

        assert response.status_code == 200
        assert parse(
            response.data['started_at']) == parse(self.start['timestamp'])
        assert parse(
            response.data['ended_at']) == parse(self.end['timestamp'])

    def test_should_calculate_duration(self, client):
        self.start['call_id'] = self.end['call_id'] = uuid.uuid4()

        client.post('/records/', self.start)
        response = client.post('/records/', self.end)

        assert response.data['duration'] == '00:30:00'

    def test_should_calculate_standard_price(self, client):
        self.start['call_id'] = self.end['call_id'] = uuid.uuid4()

        client.post('/records/', self.start)
        response = client.post('/records/', self.end)

        assert response.data['price'] == str(round(0.36 + 0.09*30, 2))

    def test_should_calculate_example_price(self, client):
        self.start['call_id'] = self.end['call_id'] = uuid.uuid4()
        self.start['timestamp'] = parse('01-01-2018 21:57:13Z').isoformat()
        self.end['timestamp'] = parse('01-01-2018 22:10:56Z').isoformat()

        client.post('/records/', self.start)
        response = client.post('/records/', self.end)

        assert response.data['price'] == '0.54'

    def test_should_calculate_reduced_price(self, client):
        self.start['call_id'] = self.end['call_id'] = uuid.uuid4()
        self.start['timestamp'] = parse('01-01-2018 22:07:13Z').isoformat()
        self.end['timestamp'] = parse('01-01-2018 22:40:56Z').isoformat()

        client.post('/records/', self.start)
        response = client.post('/records/', self.end)

        assert response.data['price'] == '0.36'

    def test_should_not_allow_start_after_end(self, client):
        self.start['call_id'] = self.end['call_id'] = uuid.uuid4()
        self.end['timestamp'] = parse('01-01-2018 22:07:13Z').isoformat()
        self.start['timestamp'] = parse('01-01-2018 22:40:56Z').isoformat()

        client.post('/records/', self.start)
        response = client.post('/records/', self.end)

        assert response.status_code == 400


def random_price():
    return decimal.Decimal(random.randrange(10000))/100


def random_duration():
    start = fake.date_time()
    return (start + delta(minutes=random.randint(0, 1000))) - start


NUMBER1 = fake_phonenumber()
NUMBER2 = fake_phonenumber()


def fake_call(start, index):
    return CallRecord(
        started_at=start,
        ended_at=start + delta(minutes=random.randint(0, 1000)),
        call_id=uuid.uuid4(),
        source=NUMBER1 if index < 10 else NUMBER2,
        destination=fake_phonenumber(),
        duration=random_duration(),
        price=random_price()
    )


@pytest.mark.django_db
class TestBills:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        calls = []

        # last but one month calls
        for i in range(15):
            calls.append(fake_call(fake.date_time_this_month(
                after_now=True, tzinfo=pytz.utc) - delta(months=2), i))

        # last month calls
        for i in range(20):
            calls.append(fake_call(fake.date_time_this_month(
                after_now=True, tzinfo=pytz.utc) - delta(months=1), i))

        # this month calls
        for i in range(10):
            calls.append(fake_call(fake.date_time_this_month(
                tzinfo=pytz.utc), i))

        CallRecord.objects.bulk_create(calls)

    def test_should_return_correct_response(self, client):
        response = client.get('/bills/non-existent/')
        assert response.status_code == 200
        assert response.data == []

    def test_should_filter_last_month(self, client):
        response = client.get('/bills/%s/' % NUMBER1)
        assert len(response.data) == 10

        response = client.get('/bills/%s/' % NUMBER2)
        assert len(response.data) == 10

    def test_should_filter_last_but_one_month(self, client):
        date = now() - delta(months=2)
        response = client.get(
            '/bills/%s/%s-%s/' % (NUMBER1, date.month, date.year))
        assert len(response.data) == 10

        response = client.get(
            '/bills/%s/%s-%s/' % (NUMBER2, date.month, date.year))
        assert len(response.data) == 5
