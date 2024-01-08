import django
from django.shortcuts import render, redirect

from core import models
from core.services import cache, meli, data


class MostExpensiveView(django.views.View):
    """Returns the base template with loading indicator for the home/most-expensive view"""

    def get(self, request):
        return render(
            request,
            "most_expensive.html",
            {
                "session": request.session,
                "force_refresh": request.GET.get("force_refresh"),
            },
        )


class MostExpensiveListView(django.views.View):
    """Returns the actual data for the most-expensive view"""

    def get(self, request):
        force_refresh = request.GET.get("force_refresh", False)
        try:
            items = data.get_most_expensive(force_refresh)
        except Exception:
            return render_error(
                request,
                "Ocurrio un error obteniendo los datos. Por favor intentalo de nuevo",
            )
        last_update = cache.most_expensive_last_update()
        return render(
            request,
            "components/most_expensive_list.html",
            {
                "items": items,
                "last_update": last_update,
            },
        )


class VendorStatsView(django.views.View):
    """Returns the base template with loading indicator for the vendors view"""

    def get(self, request):
        return render(
            request,
            "vendors.html",
            {
                "session": request.session,
                "force_refresh": request.GET.get("force_refresh"),
            },
        )


class VendorStatsTableView(django.views.View):
    """Returns the actual data for the vendors view in the form of a table"""

    def get(self, request):
        force_refresh = request.GET.get("force_refresh", False)
        try:
            vendors = data.get_vendor_stats(force_refresh)
        except Exception:
            return render_error(
                request,
                "Ocurrio un error obteniendo los datos. Por favor intentalo de nuevo",
            )
        last_update = cache.vendor_data_last_update()
        return render(
            request,
            "components/vendors_table.html",
            {
                "vendors": vendors,
                "last_update": last_update,
            },
        )


class TokenView(django.views.View):
    """This view is called by Mercadolibre after the user has logged in and authorized the app."""

    def get(self, request):
        code = request.GET.get("code", None)
        if code is None:
            return render_login_error(request)
        request.session["code"] = code
        res = meli.make_oauth_request(code)
        if "access_token" not in res:
            return render_login_error(request)

        request.session["token"] = res["access_token"]
        try:
            request.session["user"] = meli.make_user_request(res["access_token"])
            return redirect("home")
        except Exception:
            return render_login_error(request)


class LogoutView(django.views.View):
    def get(self, request):
        request.session.flush()
        next = request.GET.get("next", "home")
        return redirect(next)


def render_error(request, message):
    return render(request, "components/error.html", {"error": message})


def render_login_error(request):
    return render(request, "login_error.html")
