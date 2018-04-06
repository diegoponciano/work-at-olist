from rest_framework import serializers

from .models import CallRecord


RECORD_TYPES = [
    ('start', 'Start'),
    ('end', 'End')
]


def unset(obj, attr):
    if hasattr(obj, attr):
        delattr(obj, attr)


class RecordSerializer(serializers.ModelSerializer):
    call_id = serializers.CharField(validators=[])
    type = serializers.ChoiceField(choices=RECORD_TYPES, write_only=True)
    timestamp = serializers.DateTimeField(write_only=True)

    class Meta:
        model = CallRecord
        read_only_fields = ['started_at', 'ended_at', 'duration', 'price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if call is of type `end` excludes source and destination
        if getattr(self, 'initial_data', {}).get('type') == 'end':
            setattr(self.Meta, 'exclude', ['source', 'destination'])
            unset(self.Meta, 'fields')
        else:
            setattr(self.Meta, 'fields', '__all__')
            unset(self.Meta, 'exclude')

    def create(self, validated_data):
        MOMENTS = {
            'start': 'started_at',
            'end': 'ended_at'
        }
        moment = MOMENTS[validated_data.pop('type')]
        try:
            record = CallRecord.objects.get(call_id=validated_data['call_id'])
            setattr(record, moment, validated_data.pop('timestamp'))
            if not record.is_start_before_end():
                error_msg = 'A call cannot have started after it ended.'
                raise serializers.ValidationError({moment: error_msg})
            return self.update(record, validated_data)
        except CallRecord.DoesNotExist:
            validated_data[moment] = validated_data.pop('timestamp')
            return CallRecord.objects.create(**validated_data)


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallRecord
        exclude = ['id', 'source', 'call_id']
