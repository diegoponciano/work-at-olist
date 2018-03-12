from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import serializers

from .models import CallRecord


RECORD_TYPES = [
    ('start', 'Start'),
    ('end', 'End')
]


def get_record_serializer(data):
    serializer_types = {
        'start': StartRecordSerializer,
        'end': EndRecordSerializer
    }
    try:
        return serializer_types[data['type']]
    except (KeyError, MultiValueDictKeyError):
        raise serializers.ValidationError('errr')


class StartRecordSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=RECORD_TYPES, write_only=True)
    timestamp = serializers.DateTimeField(write_only=True)

    class Meta:
        model = CallRecord
        fields = '__all__'


class EndRecordSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=RECORD_TYPES, write_only=True)
    timestamp = serializers.DateTimeField(write_only=True)

    class Meta:
        model = CallRecord
        exclude = ['source', 'destination']
