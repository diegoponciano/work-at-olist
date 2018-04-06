from rest_framework import serializers

from .models import CallRecord


RECORD_TYPES = [
    ('start', 'Start'),
    ('end', 'End')
]


MOMENTS = {
    'start': 'started_at',
    'end': 'ended_at'
}


class RecordSerializer(serializers.ModelSerializer):
    call_id = serializers.CharField(validators=[])
    type = serializers.ChoiceField(choices=RECORD_TYPES, write_only=True)
    timestamp = serializers.DateTimeField(write_only=True)

    class Meta:
        model = CallRecord
        read_only_fields = ['started_at', 'ended_at', 'duration', 'price']
        fields = '__all__'

    def get_extra_kwargs(self, *args, **kwargs):
        if getattr(self, 'initial_data', {}).get('type') == 'end':
            return {
                'source': {'read_only': True},
                'destination': {'read_only': True}
            }
        return super().get_extra_kwargs(*args, **kwargs)

    def validate(self, data):
        try:
            instance = CallRecord.objects.get(call_id=data['call_id'])
            moment = MOMENTS[data['type']]
            setattr(instance, moment, data['timestamp'])
            if not instance.is_start_before_end():
                error_msg = 'A call cannot have started after it ended.'
                raise serializers.ValidationError({moment: error_msg})
        except CallRecord.DoesNotExist:
            pass
        return data

    def create(self, validated_data):
        moment = MOMENTS[validated_data.pop('type')]
        validated_data[moment] = validated_data.pop('timestamp')
        try:
            record = CallRecord.objects.get(
                call_id=validated_data['call_id'])
            return self.update(record, validated_data)
        except CallRecord.DoesNotExist:
            return CallRecord.objects.create(**validated_data)


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallRecord
        exclude = ['id', 'source', 'call_id']
