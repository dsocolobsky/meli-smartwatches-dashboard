from unittest import TestCase

import django

from core.models import CacheData, MeliItem, MeliVendor
from core.services import cache


class CacheTests(TestCase):
    def setUp(self):
        # Migration creates a default Cache object so we delete it for test purposes
        CacheData.objects.all().delete()
        MeliItem.objects.all().delete()
        MeliVendor.objects.all().delete()

    def test_valid_most_expensive_no_cache(self):
        self.assertFalse(cache.valid_most_expensive())

    def test_valid_most_expensive_valid_cache(self):
        self.create_cache(expensive_delta=0, vendor_delta=11)
        self.assertTrue(cache.valid_most_expensive())

    def test_valid_most_expensive_invalid_cache(self):
        self.create_cache(expensive_delta=11, vendor_delta=0)
        self.assertFalse(cache.valid_most_expensive())

    def test_valid_vendor_data_no_cache(self):
        self.assertFalse(cache.valid_vendor_data())

    def test_valid_vendor_data_valid_cache(self):
        self.create_cache(expensive_delta=11)
        self.assertTrue(cache.valid_vendor_data())

    def test_valid_vendor_data_invalid_cache(self):
        self.create_cache(vendor_delta=11)
        self.assertFalse(cache.valid_vendor_data())

    def test_most_expensive_last_update(self):
        date = django.utils.timezone.now() - django.utils.timezone.timedelta(minutes=3)
        CacheData.objects.create(
            most_expensive_cache_minutes=10,
            vendor_data_cache_minutes=10,
            most_expensive_last_update=date,
            vendor_data_last_update=django.utils.timezone.now(),
        )
        self.assertEquals(cache.most_expensive_last_update(), date)

    def test_vendor_data_last_update(self):
        date = django.utils.timezone.now() - django.utils.timezone.timedelta(minutes=3)
        CacheData.objects.create(
            most_expensive_cache_minutes=10,
            vendor_data_cache_minutes=10,
            most_expensive_last_update=django.utils.timezone.now(),
            vendor_data_last_update=date,
        )
        self.assertEquals(cache.vendor_data_last_update(), date)

    def test_most_expensive(self):
        MeliItem.objects.create(
            title="test",
            price=100,
            permalink="test",
        )
        MeliItem.objects.create(
            title="test2",
            price=200,
            permalink="test2",
        )
        self.assertEquals([c.title for c in cache.most_expensive()], ["test", "test2"])

    def test_vendor_data(self):
        MeliVendor.objects.create(
            id=1,
            name="test",
            total_items=10,
            average_price=100,
            gold_special=1,
            gold_pro=2,
        )
        MeliVendor.objects.create(
            id=2,
            name="test2",
            total_items=20,
            average_price=200,
            gold_special=3,
            gold_pro=4,
        )
        self.assertEquals([c.name for c in cache.vendor_data()], ["test", "test2"])

    def test_replace_most_expensive(self):
        self.create_cache()
        MeliItem.objects.create(
            title="test",
            price=100,
            permalink="test",
        )
        MeliItem.objects.create(
            title="test2",
            price=200,
            permalink="test2",
        )
        self.assertEquals([c.title for c in cache.most_expensive()], ["test", "test2"])
        items = [
            {
                "title": "test3",
                "price": 300,
                "permalink": "test3",
            },
            {
                "title": "test4",
                "price": 400,
                "permalink": "test4",
            },
        ]
        cache.replace_most_expensive(items)
        self.assertEquals([c.title for c in cache.most_expensive()], ["test3", "test4"])

    def test_replace_vendor_data(self):
        self.create_cache()
        MeliVendor.objects.create(
            id=1,
            name="test",
            total_items=10,
            average_price=100,
            gold_special=1,
            gold_pro=2,
        )
        MeliVendor.objects.create(
            id=2,
            name="test2",
            total_items=20,
            average_price=200,
            gold_special=3,
            gold_pro=4,
        )
        self.assertEquals([c.name for c in cache.vendor_data()], ["test", "test2"])
        data = [
            {
                "seller_id": 3,
                "seller_name": "test3",
                "total_items": 30,
                "avg_price": 300,
                "gold_special": 5,
                "gold_pro": 6,
            },
            {
                "seller_id": 4,
                "seller_name": "test4",
                "total_items": 40,
                "avg_price": 400,
                "gold_special": 7,
                "gold_pro": 8,
            },
        ]
        cache.replace_vendor_data(data)
        self.assertEquals([c.name for c in cache.vendor_data()], ["test3", "test4"])

    def create_cache(self, expensive_delta=0, vendor_delta=0):
        CacheData.objects.create(
            most_expensive_cache_minutes=10,
            vendor_data_cache_minutes=10,
            most_expensive_last_update=django.utils.timezone.now()
            - django.utils.timezone.timedelta(minutes=expensive_delta),
            vendor_data_last_update=django.utils.timezone.now()
            - django.utils.timezone.timedelta(minutes=vendor_delta),
        )
