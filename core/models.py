from datetime import datetime, timedelta

from django.db import models


class CacheData(models.Model):
    # This controls for how many minutes the cache is valid
    most_expensive_cache_minutes = models.IntegerField()
    vendor_data_cache_minutes = models.IntegerField()
    # Last timestamp when the cache was updated
    most_expensive_last_update = models.DateTimeField()
    vendor_data_last_update = models.DateTimeField()

    def is_most_expensive_cache_valid(self):
        return (
            self.most_expensive_last_update
            + timedelta(minutes=self.most_expensive_cache_minutes)
            > datetime.now()
        )

    def is_vendor_data_cache_valid(self):
        return (
            self.vendor_data_last_update
            + timedelta(minutes=self.vendor_data_cache_minutes)
            > datetime.now()
        )


class MeliItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.FloatField()
    permalink = models.URLField()

    def __str__(self):
        return self.title


class MeliVendor(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    total_items = models.IntegerField(default=0)
    average_price = models.FloatField(default=0.0)
    gold_special = models.IntegerField(default=0)
    gold_pro = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.id} - {self.name}"
