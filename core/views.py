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
        return render(
            request,
            "mas_caros.html",
            {"items": items, "last_update": cache.most_expensive_last_update},
        )


class SellerStatsView(django.views.View):
    def get(self, request):
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

        return render(request, "vendedores.html", {"sellers": data})
