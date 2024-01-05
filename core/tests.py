from unittest.mock import patch, Mock

from django.test import TestCase

from core.services.meli import MeliService


class MeliTestCase(TestCase):
    @patch("requests.get")
    def test_fetch_most_expensives(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": "true",
            "results": [
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
            ],
        }
        mock_get.return_value = mock_response
        meli = MeliService()
        items = meli.fetch_most_expensives("MLA352679", 50)
        self.assertEquals(len(items), 4)

    @patch("requests.get")
    def test_fetch_vendors_from_category(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": "true",
            "results": [
                {
                    "seller": {"id": 1},
                },
                {
                    "seller": {"id": 2},
                },
                {
                    "seller": {"id": 1},
                },
                {
                    "seller": {"id": 4},
                },
            ],
        }
        mock_get.return_value = mock_response
        meli = MeliService()
        vendors = meli.fetch_vendors_from_category("MLA352679", 50)
        self.assertEquals(vendors, {1, 2, 4})

    @patch("requests.get")
    def test_fetch_vendor_data(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": "true",
            "seller": {"nickname": "test"},
            "paging": {"total": 10},
            "results": [
                {
                    "price": 100,
                    "listing_type_id": "gold_special",
                },
                {
                    "price": 200,
                    "listing_type_id": "gold_pro",
                },
                {
                    "price": 300,
                },
                {
                    "price": 400,
                },
            ],
        }
        mock_get.return_value = mock_response
        meli = MeliService()
        vendor_data = meli.fetch_vendor_data(1)
        self.assertEquals(vendor_data["seller_id"], 1)
        self.assertEquals(vendor_data["seller_name"], "test")
        self.assertEquals(vendor_data["total_items"], 10)
        self.assertEquals(vendor_data["gold_special"], 1)
        self.assertEquals(vendor_data["gold_pro"], 1)
        self.assertEquals(vendor_data["avg_price"], 1000 / 10)
