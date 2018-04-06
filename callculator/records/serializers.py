from rest_framework import serializers

from .models import CallRecord


RECORD_TYPES = [
    ('start', 'Start'),
    ('end', 'End')
]


class RecordSerializer(serializers.ModelSerializer):
    call_id = serializers.CharField(validators=[])
    type = serializers.ChoiceField(choices=RECORD_TYPES, write_only=True)
    timestamp = serializers.DateTimeField(write_only=True)

    class Meta:
        model = CallRecord
        fields = '__all__'
        read_only_fields = ['started_at', 'ended_at', 'duration', 'price']

    def get_extra_kwargs(self, *args, **kwargs):
        try:
            if self.initial_data['type'] == 'end':
                return {
                    'source': {'read_only': True},
                    'destination': {'read_only': True}
                }
        except (AttributeError, KeyError):
            pass
        return super().get_extra_kwargs(*args, **kwargs)

    def create(self, validated_data):
        MOMENTS = {
            'start': 'started_at',
            'end': 'ended_at'
        }
        moment = validated_data.pop('type')
        try:
            record = CallRecord.objects.get(call_id=validated_data['call_id'])
            setattr(record, MOMENTS[moment], validated_data.pop('timestamp'))
            if not record.is_start_before_end():
                error_msg = 'A call cannot start after the end.'
                raise serializers.ValidationError(error_msg)
            return self.update(record, validated_data)
        except CallRecord.DoesNotExist:
            validated_data[MOMENTS[moment]] = validated_data.pop('timestamp')
            return CallRecord.objects.create(**validated_data)


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallRecord
        exclude = ['id', 'source', 'call_id']
