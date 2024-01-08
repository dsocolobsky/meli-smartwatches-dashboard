from unittest.mock import patch

from django.test import TestCase, override_settings


MOCK_ITEMS = [
    {
        "title": "item1",
        "price": 100,
        "permalink": "https://url1.com",
    },
    {
        "title": "item2",
        "price": 200,
        "permalink": "https://url2.com",
    },
]

MOCK_VENDORS = [
    {
        "id": 1,
        "name": "vendor1",
        "total_items": 10,
        "average_price": 100,
        "gold_special": 1,
        "gold_pro": 1,
    },
    {
        "id": 2,
        "name": "vendor2",
        "total_items": 20,
        "average_price": 200,
        "gold_special": 2,
        "gold_pro": 2,
    },
]


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
)
class ViewsTests(TestCase):
    @patch("core.services.data.get_most_expensive", return_value=MOCK_ITEMS)
    def test_homepage(self, get_most_expensive):
        get_most_expensive.return_value = MOCK_ITEMS

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Smartwatches más caros")
        self.assertContains(response, "Por favor espere")
        self.assertNotContains(response, "item1")

    @patch("core.services.data.get_most_expensive", return_value=MOCK_ITEMS)
    def test_most_expensive_view(self, get_most_expensive):
        get_most_expensive.return_value = MOCK_ITEMS

        response = self.client.get("/most-expensive/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Smartwatches más caros")
        self.assertContains(response, "Por favor espere")
        self.assertNotContains(response, "item1")

    @patch("core.services.data.get_most_expensive", return_value=MOCK_ITEMS)
    def test_most_expensive_list_view(self, get_most_expensive):
        get_most_expensive.return_value = MOCK_ITEMS

        response = self.client.get("/most-expensive-list/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "item1")
        self.assertContains(response, "item2")
        self.assertContains(response, "https://url1.com")
        self.assertContains(response, "https://url2.com")
        self.assertNotContains(response, "Por favor espere")

    @patch("core.services.data.get_most_expensive", side_effect=Exception)
    def test_most_expensive_error(self, get_most_expensive):
        get_most_expensive.side_effect = Exception

        response = self.client.get("/most-expensive-list/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ocurrio un error obteniendo los datos")
        self.assertNotContains(response, "Por favor espere")
        self.assertNotContains(response, "item1")

    @patch("core.services.data.get_vendor_stats", return_value=MOCK_VENDORS)
    def test_vendors_view(self, get_vendor_stats):
        get_vendor_stats.return_value = MOCK_VENDORS

        response = self.client.get("/vendors/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vendedores con mas items")
        self.assertContains(response, "Por favor espere")
        self.assertNotContains(response, "vendor1")

    @patch("core.services.data.get_vendor_stats", return_value=MOCK_VENDORS)
    def test_vendors_table_view(self, get_vendor_stats):
        get_vendor_stats.return_value = MOCK_VENDORS

        response = self.client.get("/vendors-table/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "vendor1")
        self.assertContains(response, "vendor2")
        self.assertNotContains(response, "Por favor espere")

    @patch("core.services.data.get_vendor_stats", side_effect=Exception)
    def test_vendors_error(self, get_vendor_stats):
        get_vendor_stats.side_effect = Exception

        response = self.client.get("/vendors-table/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ocurrio un error obteniendo los datos")
        self.assertNotContains(response, "Por favor espere")
        self.assertNotContains(response, "vendor1")

    @patch("core.services.meli.make_oauth_request")
    @patch("core.services.meli.make_user_request")
    def test_token_view(self, make_user_request, make_oauth_request):
        make_oauth_request.return_value = {
            "access_token": "APP_USR-1234",
            "token_type": "Bearer",
            "expires_in": 21600,
            "scope": "read",
            "user_id": 123,
        }

        user = {
            "nickname": "test",
            "first_name": "Test",
            "last_name": "Testing",
            "permalink": "https://example.com",
        }
        make_user_request.return_value = user

        response = self.client.get("/token/?code=1234")
        self.assertEqual(response.status_code, 302)

        self.assertEquals(self.client.session["code"], "1234")
        self.assertEqual(self.client.session["token"], "APP_USR-1234")
        self.assertEqual(self.client.session["user"], user)

    @patch("core.services.meli.make_oauth_request", side_effect=Exception)
    def test_token_view_error(self, make_oauth_request):
        make_oauth_request.side_effect = Exception
        response = self.client.get("/token/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ocurrio un error loggeandote")

    def test_logout_view(self):
        self.client.session["code"] = "1234"
        self.client.session["token"] = "APP_USR-1234"
        self.client.session["user"] = {
            "nickname": "test",
            "first_name": "Test",
            "last_name": "Testing",
            "permalink": "https://example.com",
        }

        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 302)

        self.assertNotIn("code", self.client.session)
        self.assertNotIn("token", self.client.session)
        self.assertNotIn("user", self.client.session)
