import django
from django.shortcuts import render

from core import models
from core.services.meli import MeliService


class HomeView(django.views.View):
    def get(self, request):
        cache = models.CacheData.objects.first()
        if cache and cache.is_most_expensive_cache_valid():
            print("Cache is valid, using")
            items = models.MeliItem.objects.all()
            return render(
                request,
                "mas_caros.html",
                {"items": items, "last_update": cache.most_expensive_last_update},
            )

        print("Cache is invalid, fetching")
        try:
            items = MeliService().fetch_most_expensives("MLA352679", 50)
        except Exception:
            return render(request, "error.html")
        # Delete all old data and persist newly fetched items
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
        # Update the cache timestamp
        cache.most_expensive_last_update = django.utils.timezone.now()
        cache.save()
        items = models.MeliItem.objects.all()
        return render(
            request,
            "mas_caros.html",
            {"items": items, "last_update": cache.most_expensive_last_update},
        )


class SellerStatsView(django.views.View):
    def get(self, request):
        cache = models.CacheData.objects.first()
        if cache and cache.is_vendor_data_cache_valid():
            print("Cache is valid, using")
            sellers = models.MeliVendor.objects.all()
            return render(
                request,
                "vendedores.html",
                {"sellers": sellers, "last_update": cache.vendor_data_last_update},
            )

        print("Cache is invalid, fetching")
        # Get the first 1000 items from the Smartwatch category
        meli = MeliService()
        try:
            # TODO update the limit
            vendor_ids = meli.fetch_vendors_from_category("MLA352679", 50)
        except Exception:
            return render(request, "error.html")
        data = []
        for vendor_id in vendor_ids:
            data.append(meli.fetch_vendor_data(vendor_id))
        # Sort by total items desc
        data.sort(key=lambda x: x["total_items"], reverse=True)

        # Delete all old data and persist newly fetched items
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
        # Update the cache timestamp
        cache.vendor_data_last_update = django.utils.timezone.now()
        cache.save()

        vendors = models.MeliVendor.objects.all()
        return render(
            request,
            "vendedores.html",
            {"sellers": vendors, "last_update": cache.vendor_data_last_update},
        )
