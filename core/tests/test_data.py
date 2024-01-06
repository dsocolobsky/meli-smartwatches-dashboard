from unittest import TestCase
from unittest.mock import patch

import django

from core.models import CacheData, MeliItem, MeliVendor
from core.services import data


class DataTests(TestCase):
    def setUp(self):
        # Migration creates a default Cache object so we delete it for test purposes
        CacheData.objects.all().delete()
        MeliItem.objects.all().delete()
        MeliVendor.objects.all().delete()

    @patch("core.services.meli.fetch_most_expensive")
    def test_get_most_expensive_valid_cache(self, meli_fetch):
        self.create_cache(expensive_delta=0)
        item = MeliItem.objects.create(
            title="test",
            price=100,
            permalink="https://test.com",
        )
        self.assertEquals(len(data.get_most_expensive()), 1)
        self.assertEquals(item, data.get_most_expensive()[0])
        self.assertEquals(meli_fetch.call_count, 0)

    @patch("core.services.meli.fetch_most_expensive")
    def test_get_more_expensive_invalid_cache(self, meli_fetch):
        self.create_cache(expensive_delta=11)
        self.assertFalse(CacheData.objects.first().is_most_expensive_cache_valid())
        item = MeliItem.objects.create(
            title="test",
            price=100,
            permalink="https://test.com",
        )
        meli_fetch.return_value = [
            {
                "title": "Item 1",
                "price": 100,
                "permalink": "https://item1.com",
            },
            {
                "title": "Item 2",
                "price": 200,
                "permalink": "https://item2.com",
            },
            {
                "title": "Item 3",
                "price": 300,
                "permalink": "https://item3.com",
            },
            {
                "title": "Item 4",
                "price": 400,
                "permalink": "https://item4.com",
            },
        ]
        res = data.get_most_expensive()
        self.assertEquals([c.price for c in res], [100, 200, 300, 400])
        self.assertEquals(meli_fetch.call_count, 1)
        # Ensure the cache was updated with the new values
        in_db = MeliItem.objects.all()
        self.assertEquals([c.price for c in in_db], [100, 200, 300, 400])
        # Ensure the last update was updated
        self.assertTrue(CacheData.objects.first().is_most_expensive_cache_valid())

    @patch("core.services.meli.fetch_vendors_from_category")
    def test_get_vendors_from_category_valid_cache(self, meli_fetch):
        self.create_cache(vendor_delta=0)
        vendor = MeliVendor.objects.create(
            id=1,
            name="Vendor 1",
            total_items=10,
            average_price=100,
            gold_special=1,
            gold_pro=2,
        )
        vendors = data.get_vendor_stats()
        self.assertEquals([c for c in vendors], [vendor])
        self.assertEquals(meli_fetch.call_count, 0)

    @patch("core.services.meli.fetch_vendors_from_category")
    @patch("core.services.meli.fetch_vendor_data")
    def test_get_vendors_from_category_invalid_cache(
        self, meli_fetch_data, meli_fetch_vendors
    ):
        self.create_cache(vendor_delta=11)
        self.assertFalse(CacheData.objects.first().is_vendor_data_cache_valid())
        MeliVendor.objects.create(
            id=1,
            name="Vendor 1",
            total_items=10,
            average_price=100,
            gold_special=1,
            gold_pro=2,
        )
        meli_fetch_vendors.return_value = {2}
        meli_fetch_data.return_value = {
            "seller_id": 2,
            "seller_name": "Vendor 2",
            "total_items": 20,
            "avg_price": 200,
            "gold_special": 2,
            "gold_pro": 4,
        }

        res = data.get_vendor_stats()
        self.assertEquals([c.id for c in res], [2])
        self.assertEquals(meli_fetch_vendors.call_count, 1)
        self.assertEquals(meli_fetch_data.call_count, 1)
        # Ensure the cache was updated with the new values
        in_db = MeliVendor.objects.all()
        self.assertEquals([c.id for c in in_db], [2])
        # Ensure the last update was updated
        self.assertTrue(CacheData.objects.first().is_vendor_data_cache_valid())

    def create_cache(self, expensive_delta=0, vendor_delta=0):
        CacheData.objects.create(
            most_expensive_cache_minutes=10,
            vendor_data_cache_minutes=10,
            most_expensive_last_update=django.utils.timezone.now()
            - django.utils.timezone.timedelta(minutes=expensive_delta),
            vendor_data_last_update=django.utils.timezone.now()
            - django.utils.timezone.timedelta(minutes=vendor_delta),
        )
