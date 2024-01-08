from typing import Any

import django
from django.utils.timezone import datetime

from core import models


def valid_most_expensive() -> bool:
    cache = models.CacheData.objects.first()
    return cache and cache.is_most_expensive_cache_valid()


def valid_vendor_data() -> bool:
    cache = models.CacheData.objects.first()
    return cache and cache.is_vendor_data_cache_valid()


def most_expensive_last_update() -> datetime:
    cache = models.CacheData.objects.first()
    return cache.most_expensive_last_update


def vendor_data_last_update() -> datetime:
    cache = models.CacheData.objects.first()
    return cache.vendor_data_last_update


def most_expensive() -> list[models.MeliItem]:
    return models.MeliItem.objects.all().order_by("-price")


def vendor_data() -> list[models.MeliVendor]:
    return models.MeliVendor.objects.all().order_by("-total_items")


def replace_most_expensive(items: list[dict[str, Any]]) -> None:
    cache = __get_or_create_cache()
    models.MeliItem.objects.all().delete()
    models.MeliItem.objects.bulk_create(
        [
            models.MeliItem(
                title=item["title"],
                price=item["price"],
                permalink=item["permalink"],
            )
            for item in items
        ]
    )
    cache.most_expensive_last_update = django.utils.timezone.now()
    cache.save()


def replace_vendor_data(data: list[dict]) -> None:
    cache = __get_or_create_cache()
    models.MeliVendor.objects.all().delete()
    models.MeliVendor.objects.bulk_create(
        [
            models.MeliVendor(
                id=item["seller_id"],
                name=item["seller_name"],
                total_items=item["total_items"],
                average_price=item["avg_price"],
                gold_special=item["gold_special"],
                gold_pro=item["gold_pro"],
            )
            for item in data
        ]
    )
    cache.vendor_data_last_update = django.utils.timezone.now()
    cache.save()


def __get_or_create_cache():
    cache = models.CacheData.objects.first()
    if not cache:
        cache = models.CacheData.objects.create(
            most_expensive_last_update=django.utils.timezone.now(),
            vendor_data_last_update=django.utils.timezone.now(),
        )
    return cache
