from datetime import datetime, timedelta

from django.db import models

from smartwatches import settings


class CacheData(models.Model):
    # Last timestamp when the cache was updated
    most_expensive_last_update = models.DateTimeField()
    vendor_data_last_update = models.DateTimeField()

    def is_most_expensive_cache_valid(self):
        return (
            self.most_expensive_last_update
            + timedelta(minutes=settings.MOST_EXPENSIVE_CACHE_MINUTES)
            > datetime.now()
        )

    def is_vendor_data_cache_valid(self):
        return (
            self.vendor_data_last_update
            + timedelta(minutes=settings.VENDORS_CACHE_MINUTES)
            > datetime.now()
        )


class MeliItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.FloatField()
    permalink = models.URLField()
    thumbnail = models.URLField(blank=True, null=True, default=None)

    class Meta:
        ordering = ["-price"]

    def __str__(self):
        return self.title


class MeliVendor(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    total_items = models.IntegerField(default=0)
    average_price = models.FloatField(default=0.0)
    gold_special = models.IntegerField(default=0)
    gold_pro = models.IntegerField(default=0)

    class Meta:
        ordering = ["-total_items"]

    def __str__(self):
        return f"{self.id} - {self.name}"
