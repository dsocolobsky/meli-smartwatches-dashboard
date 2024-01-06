import django
from django.shortcuts import render, redirect

from core import models
from core.services import cache, meli, data


class HomeView(django.views.View):
    def get(self, request):
        items = data.get_most_expensive()
        last_update = cache.most_expensive_last_update()
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
        vendors = data.get_vendor_stats()
        last_update = cache.vendor_data_last_update()
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
