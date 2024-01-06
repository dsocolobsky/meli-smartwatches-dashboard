import concurrent.futures


from core import models
from core.services import cache, meli


def get_most_expensive() -> list[models.MeliItem]:
    if cache.valid_most_expensive():
        print("Cache is valid, using")
        return cache.most_expensive()

    print("Cache is invalid, fetching")
    try:
        items = meli.fetch_most_expensive("MLA352679", 50)
    except Exception:
        raise Exception("Items could not be fetched")
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
    print(f"Fetching page {page}")
    return meli.fetch_vendors_from_category("MLA352679", 50, page * 50)


def fetch_vendor_data(vendor_id: int):
    print(f"Fetching vendor data for {vendor_id}")
    return meli.fetch_vendor_data(vendor_id)
