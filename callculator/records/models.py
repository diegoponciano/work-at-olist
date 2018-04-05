from datetime import timedelta
from django.conf import settings
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
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def calculate_duration(self):
        self.duration = self.ended_at - self.started_at

    def standard_minutes(self):
        minutes = 0
        current = self.started_at
        end = self.ended_at

        while current < end:
            day_start = current.replace(hour=settings.START_HOUR, minute=0,
                                        second=0, microsecond=0)
            day_end = current.replace(hour=settings.END_HOUR, minute=0,
                                      second=0, microsecond=0)
            if current >= day_end:
                current = current.replace(hour=0, minute=0, second=0,
                                          microsecond=0) + timedelta(1)
                break
            if end < day_end:
                day_end = end
            if current > day_start:
                day_start = current
            minutes += (day_end - day_start).seconds // 60
            current = current.replace(hour=0, minute=0, second=0,
                                      microsecond=0) + timedelta(1)
        return minutes

    def calculate_price(self):
        self.price = (
            settings.STANDING_CHARGE +
            (self.standard_minutes() * settings.MINUTELY_PRICE))


@receiver(pre_save, sender=CallRecord)
def calculate_price_and_duration(sender, instance, **kwargs):
    if instance.started_at and instance.ended_at:
        instance.calculate_duration()
        instance.calculate_price()
