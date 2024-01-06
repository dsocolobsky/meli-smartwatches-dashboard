from core import models
from core.services import cache, meli
from django.utils.timezone import datetime


def get_most_expensive() -> list[models.MeliItem]:
    if cache.valid_most_expensive():
        print("Cache is valid, using")
        return cache.most_expensive()

    print("Cache is invalid, fetching")
    try:
        items = meli.fetch_most_expensive("MLA352679", 50)
    except Exception:
        return models.MeliItem.objects.none()
    # Delete all old data and persist newly fetched items
    cache.replace_most_expensive(items)
    return cache.most_expensive()


def get_vendor_stats() -> list[models.MeliVendor]:
    if cache.valid_vendor_data():
        print("Cache is valid, using")
        return cache.vendor_data()

    print("Cache is invalid, fetching")
    # Get the first 1000 items from the Smartwatch category
    try:
        # TODO update the limit
        vendor_ids = meli.fetch_vendors_from_category("MLA352679", 50)
    except Exception:
        return models.MeliVendor.objects.none()
    data = []
    for vendor_id in vendor_ids:
        vendor_data = meli.fetch_vendor_data(vendor_id)
        data.append(vendor_data)
    # Sort by total items desc
    data.sort(key=lambda x: x["total_items"], reverse=True)

    # Delete all old data and persist newly fetched items
    cache.replace_vendor_data(data)
    return cache.vendor_data()
