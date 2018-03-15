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


class RecordSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=RECORD_TYPES, write_only=True)
    call_id = serializers.CharField(validators=[])

    class Meta:
        model = CallRecord
        fields = '__all__'

    def create(self, validated_data):
        validated_data.pop('type', None)
        try:
            record = CallRecord.objects.get(call_id=validated_data['call_id'])
            return self.update(record, validated_data)
        except CallRecord.DoesNotExist:
            return CallRecord.objects.create(**validated_data)


class StartRecordSerializer(RecordSerializer):
    timestamp = serializers.DateTimeField(source='started_at', write_only=True)


class EndRecordSerializer(RecordSerializer):
    timestamp = serializers.DateTimeField(source='ended_at', write_only=True)

    class Meta:
        model = CallRecord
        exclude = ['source', 'destination']
