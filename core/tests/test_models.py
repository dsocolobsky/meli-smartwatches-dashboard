from django.test import TestCase

import django

from core.models import MeliItem, MeliVendor, CacheData


class ModelTests(TestCase):
    def setUp(self):
        # Migration creates a default Cache object so we delete it for test purposes
        CacheData.objects.all().delete()
        MeliItem.objects.all().delete()
        MeliVendor.objects.all().delete()

    def test_create_meli_item(self):
        self.assertEquals(MeliItem.objects.count(), 0)
        item = MeliItem.objects.create(
            title="Item 1",
            price=100,
            permalink="https://item1.com",
        )
        self.assertEqual(item.title, "Item 1")
        self.assertEqual(item.price, 100)
        self.assertEqual(item.permalink, "https://item1.com")
        self.assertEquals(MeliItem.objects.count(), 1)

    def test_create_vendor(self):
        self.assertEquals(MeliVendor.objects.count(), 0)
        vendor = MeliVendor.objects.create(
            id=1,
            name="Vendor 1",
            total_items=10,
            average_price=100,
            gold_special=1,
            gold_pro=2,
        )
        self.assertEqual(vendor.id, 1)
        self.assertEqual(vendor.name, "Vendor 1")
        self.assertEqual(vendor.total_items, 10)
        self.assertEqual(vendor.average_price, 100)
        self.assertEqual(vendor.gold_special, 1)
        self.assertEqual(vendor.gold_pro, 2)
        self.assertEquals(MeliVendor.objects.count(), 1)

    def test_create_valid_cache_data(self):
        self.assertEquals(CacheData.objects.count(), 0)
        cache = CacheData.objects.create(
            most_expensive_last_update=django.utils.timezone.now(),
            vendor_data_last_update=django.utils.timezone.now(),
        )
        self.assertTrue(cache.is_most_expensive_cache_valid())
        self.assertTrue(cache.is_vendor_data_cache_valid())
        self.assertEquals(CacheData.objects.count(), 1)

    def test_create_invalid_cache_data(self):
        self.assertEquals(CacheData.objects.count(), 0)
        cache = CacheData.objects.create(
            most_expensive_last_update=django.utils.timezone.now()
            - django.utils.timezone.timedelta(minutes=6),
            vendor_data_last_update=django.utils.timezone.now()
            - django.utils.timezone.timedelta(minutes=6),
        )
        self.assertFalse(cache.is_most_expensive_cache_valid())
        self.assertFalse(cache.is_vendor_data_cache_valid())
        self.assertEquals(CacheData.objects.count(), 1)
