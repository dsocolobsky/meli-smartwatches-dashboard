from unittest.mock import patch

from django.test import TestCase

import django

from core.models import MeliItem, CacheData, MeliVendor


class ViewsTests(TestCase):
    def setUp(self):
        CacheData.objects.all().delete()
        MeliItem.objects.all().delete()
        MeliVendor.objects.all().delete()

        CacheData.objects.create(
            most_expensive_cache_minutes=10,
            vendor_data_cache_minutes=10,
            most_expensive_last_update=django.utils.timezone.now(),
            vendor_data_last_update=django.utils.timezone.now(),
        )
        MeliItem.objects.create(
            title="item1",
            price=100,
            permalink="https://url1.com",
        )
        MeliItem.objects.create(
            title="item2",
            price=200,
            permalink="https://url2.com",
        )
        MeliVendor.objects.create(
            id=1,
            name="vendor1",
            total_items=10,
            average_price=100,
            gold_special=1,
            gold_pro=1,
        )
        MeliVendor.objects.create(
            id=2,
            name="vendor2",
            total_items=20,
            average_price=200,
            gold_special=2,
            gold_pro=2,
        )

    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Smartwatches más caros")
        self.assertContains(response, "Por favor espere")
        self.assertNotContains(response, "item1")

    def test_most_expensive_view(self):
        response = self.client.get("/most-expensive/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Smartwatches más caros")
        self.assertContains(response, "Por favor espere")
        self.assertNotContains(response, "item1")

    def test_most_expensive_list_view(self):
        response = self.client.get("/most-expensive-list/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "item1")
        self.assertContains(response, "item2")
        self.assertContains(response, "https://url1.com")
        self.assertContains(response, "https://url2.com")
        self.assertNotContains(response, "Por favor espere")

    def test_vendors_view(self):
        response = self.client.get("/vendors/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vendedores con mas items")
        self.assertContains(response, "Por favor espere")
        self.assertNotContains(response, "vendor1")

    def test_vendors_table_view(self):
        response = self.client.get("/vendors-table/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "vendor1")
        self.assertContains(response, "vendor2")
        self.assertNotContains(response, "Por favor espere")

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
