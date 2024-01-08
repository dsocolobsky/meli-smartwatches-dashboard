import django
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page

from core.services import meli, data


class MostExpensiveView(django.views.View):
    """Returns the base template with loading indicator for the home/most-expensive view"""

    def get(self, request):
        return render(
            request,
            "most_expensive.html",
            {
                "session": request.session,
            },
        )


class MostExpensiveListView(django.views.View):
    """Returns the actual data for the most-expensive view"""

    def get(self, request):
        try:
            items = data.get_most_expensive()
        except Exception:
            return render_error(
                request,
                "Ocurrio un error obteniendo los datos. Por favor intentalo de nuevo",
            )
        return render(
            request,
            "components/most_expensive_list.html",
            {
                "items": items,
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
            },
        )


class VendorStatsTableView(django.views.View):
    """Returns the actual data for the vendors view in the form of a table"""

    def get(self, request):
        try:
            vendors = data.get_vendor_stats()
        except Exception:
            return render_error(
                request,
                "Ocurrio un error obteniendo los datos. Por favor intentalo de nuevo",
            )
        return render(
            request,
            "components/vendors_table.html",
            {
                "vendors": vendors,
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
