import django
from django.shortcuts import render

from core.services.meli import MeliService


class HomeView(django.views.View):
    def get(self, request):
        try:
            items = MeliService().fetch_most_expensives("MLA352679", 50)
        except Exception:
            return render(request, "error.html")
        return render(request, "mas_caros.html", {"items": items})


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
