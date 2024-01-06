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
            title="test",
            price=100,
            permalink="https://test.com",
        )
        MeliItem.objects.create(
            title="test2",
            price=200,
            permalink="https://test2.com",
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
        self.assertContains(response, "test")
        self.assertContains(response, "test2")
        self.assertContains(response, "https://test.com")
        self.assertContains(response, "https://test2.com")

    def test_vendors_view(self):
        response = self.client.get("/vendors/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "vendor1")
        self.assertContains(response, "vendor2")

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
