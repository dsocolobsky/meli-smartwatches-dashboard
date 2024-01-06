import django
from django.shortcuts import render, redirect

from core import models
from core.services import cache, meli


class HomeView(django.views.View):
    def get(self, request):
        if cache.valid_most_expensive():
            print("Cache is valid, using")
            items = models.MeliItem.objects.all()
            return render(
                request,
                "mas_caros.html",
                {
                    "items": items,
                    "last_update": cache.most_expensive_last_update(),
                    "session": request.session,
                },
            )

        print("Cache is invalid, fetching")
        try:
            items = meli.fetch_most_expensive("MLA352679", 50)
        except Exception:
            return render(request, "error.html")
        # Delete all old data and persist newly fetched items
        last_update = cache.replace_most_expensive(items)
        items = models.MeliItem.objects.all()
        return render(
            request,
            "mas_caros.html",
            {
                "items": items,
                "last_update": last_update,
                "session": request.session,
            },
        )


class SellerStatsView(django.views.View):
    def get(self, request):
        if cache.valid_vendor_data():
            print("Cache is valid, using")
            sellers = models.MeliVendor.objects.all()
            return render(
                request,
                "vendedores.html",
                {
                    "sellers": sellers,
                    "last_update": cache.vendor_data_last_update(),
                    "session": request.session,
                },
            )

        print("Cache is invalid, fetching")
        # Get the first 1000 items from the Smartwatch category
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
        last_update = cache.replace_vendor_data(data)

        vendors = models.MeliVendor.objects.all()
        return render(
            request,
            "vendedores.html",
            {
                "sellers": vendors,
                "last_update": last_update,
                "session": request.session,
            },
        )


class TokenView(django.views.View):
    def get(self, request):
        code = request.GET.get("code", None)
        print(f"Code: {code}")
        if code is None:
            return render(request, "error.html")
        request.session["code"] = code
        res = meli.make_oauth_request(code)
        if "access_token" not in res:
            return render(request, "error.html")

        request.session["token"] = res["access_token"]
        try:
            request.session["user"] = meli.make_user_request(res["access_token"])
            return redirect("home")
        except Exception:
            return render(request, "error.html")


class LogoutView(django.views.View):
    def get(self, request):
        request.session.flush()
        next = request.GET.get("next", "home")
        return redirect(next)
