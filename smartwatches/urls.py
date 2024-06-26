"""
URL configuration for smartwatches project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.decorators.cache import cache_page

from core.views import (
    MostExpensiveView,
    MostExpensiveListView,
    VendorStatsView,
    TokenView,
    LogoutView,
    VendorStatsTableView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("vendors/", VendorStatsView.as_view(), name="vendors"),
    path(
        "vendors-table/",
        cache_page(60 * 5)(VendorStatsTableView.as_view()),
        name="vendors_table",
    ),
    path("token/", TokenView.as_view(), name="token"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "most-expensive-list/",
        cache_page(60 * 5)(MostExpensiveListView.as_view()),
        name="most_expensive_list",
    ),
    path("most-expensive/", MostExpensiveView.as_view(), name="most_expensive"),
    path("", MostExpensiveView.as_view(), name="home"),  # Handle / as /most-expensive/
]
