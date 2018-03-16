from datetime import timedelta
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


MINUTELY_PRICE = 0.09
STANDING_CHARGE = 0.36


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
            day_start = current.replace(hour=6, minute=0, second=0,
                                        microsecond=0)
            day_end = current.replace(hour=22, minute=0, second=0,
                                      microsecond=0)
            if current >= day_end:
                current = current.replace(hour=0, minute=0, second=0,
                                          microsecond=0) + timedelta(1)
                continue
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
            STANDING_CHARGE + (self.standard_minutes() * MINUTELY_PRICE))


@receiver(pre_save, sender=CallRecord)
def calculate_price_and_duration(sender, instance, **kwargs):
    if instance.started_at and instance.ended_at:
        instance.calculate_duration()
        instance.calculate_price()
