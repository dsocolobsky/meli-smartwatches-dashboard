import concurrent.futures


from core import models
from core.services import cache, meli


def get_most_expensive(force_refresh: bool = False) -> list[models.MeliItem]:
    if not force_refresh and cache.valid_most_expensive():
        return cache.most_expensive()  # Valid cache => use DB data and skip

    # Cache was Invalid
    try:
        items = meli.fetch_most_expensive("MLA352679", 20)
    except Exception:
        raise Exception("Items could not be fetched")
    # Delete all old data and persist newly fetched items
    cache.replace_most_expensive(items)
    return cache.most_expensive()


def get_vendor_stats(force_refresh: bool = False) -> list[models.MeliVendor]:
    if not force_refresh and cache.valid_vendor_data():
        return cache.vendor_data()  # Valid cache => use DB data and skip

    # Cache was Invalid
    # Get the first 1000 items from the Smartwatch category
    try:
        vendor_ids = set()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(fetch_vendor_ids, range(19)))

        vendor_ids = set().union(*results)
    except Exception as e:
        print(e)

    if len(vendor_ids) == 0:
        raise Exception("Vendors could not be fetched")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        data = list(executor.map(fetch_vendor_data, vendor_ids))

    # Delete all old data and persist newly fetched items
    cache.replace_vendor_data(data)
    return cache.vendor_data()


def fetch_vendor_ids(page: int) -> set[int]:
    return meli.fetch_vendors_from_category("MLA352679", 50, page * 50)


def fetch_vendor_data(vendor_id: int):
    return meli.fetch_vendor_data(vendor_id)
