from django.db import models


class CallRecord(models.Model):
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    call_id = models.CharField(max_length=250, unique=True)
    source = models.CharField(max_length=20)
    destination = models.CharField(max_length=20)
    duration = models.DurationField(null=True)
