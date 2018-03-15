from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


class CallRecord(models.Model):
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    call_id = models.CharField(max_length=250, unique=True)
    source = models.CharField(max_length=20)
    destination = models.CharField(max_length=20)
    duration = models.DurationField(null=True)


@receiver(pre_save, sender=CallRecord)
def calculate_duration(sender, instance, **kwargs):
    if instance.started_at and instance.ended_at:
        instance.duration = instance.ended_at - instance.started_at
