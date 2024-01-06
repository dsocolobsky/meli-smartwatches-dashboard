from unittest.mock import patch, Mock

from django.test import TestCase
from core.services import meli


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
        items = meli.fetch_most_expensive("MLA352679", 50)
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
        vendor_data = meli.fetch_vendor_data(1)
        self.assertEquals(vendor_data["seller_id"], 1)
        self.assertEquals(vendor_data["seller_name"], "test")
        self.assertEquals(vendor_data["total_items"], 10)
        self.assertEquals(vendor_data["gold_special"], 1)
        self.assertEquals(vendor_data["gold_pro"], 1)
        self.assertEquals(vendor_data["avg_price"], 1000 / 10)

    @patch("requests.post")
    def test_make_oauth_request(self, mock_post):
        mock_response = Mock()
        expected = {
            "access_token": "TOK_TEST",
            "token_type": "bearer",
            "expires_in": 1000,
            "scope": "test",
            "user_id": 1,
            "refresh_token": "test",
        }
        mock_response.json.return_value = expected
        mock_post.return_value = mock_response
        response = meli.make_oauth_request("some_code")

        self.assertEquals(response, expected)

    @patch("requests.get")
    def test_make_user_request(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 1,
            "nickname": "nick",
            "email": "somemail@example.com",
            "first_name": "first",
            "last_name": "last",
            "country_id": "AR",
            "permalink": "http://example.com",
        }
        mock_get.return_value = mock_response
        response = meli.make_user_request("TOK_TEST")
        self.assertEquals(
            response,
            {
                "nickname": "nick",
                "first_name": "first",
                "last_name": "last",
                "permalink": "http://example.com",
            },
        )

    @patch("requests.get")
    def test_make_user_request_no_token(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 1,
            "nickname": "nick",
            "email": "somemail@example.com",
            "first_name": "first",
            "last_name": "last",
            "country_id": "AR",
            "permalink": "http://example.com",
        }
        mock_get.return_value = mock_response
        response = meli.make_user_request(None)
        self.assertEquals(response, None)
