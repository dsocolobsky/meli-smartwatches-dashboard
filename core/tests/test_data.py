from django.test import TestCase
from unittest.mock import patch

from core.services import data


class DataTests(TestCase):
    @patch("core.services.meli.fetch_most_expensive")
    def test_get_more_expensive(self, meli_fetch):
        meli_fetch.return_value = [
            {
                "title": "Item 1",
                "price": 100,
                "permalink": "https://item1.com",
            },
            {
                "title": "Item 2",
                "price": 600,
                "permalink": "https://item2.com",
            },
            {
                "title": "Item 3",
                "price": 200,
                "permalink": "https://item3.com",
            },
            {
                "title": "Item 4",
                "price": 400,
                "permalink": "https://item4.com",
            },
        ]
        res = data.get_most_expensive()
        self.assertEquals([c["price"] for c in res], [600, 400, 200, 100])
        self.assertEquals(meli_fetch.call_count, 1)

    @patch("core.services.meli.fetch_vendors_from_category")
    @patch("core.services.meli.fetch_vendor_data")
    def test_get_vendors_from_category_invalid_cache(
        self, meli_fetch_data, meli_fetch_vendors
    ):
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
        self.assertEquals([c["id"] for c in res], [2])
        self.assertEquals(meli_fetch_vendors.call_count, 19)
        self.assertEquals(meli_fetch_data.call_count, 1)
