import concurrent.futures

from core.services import meli


def get_most_expensive() -> list[dict[str, str | int]]:
    try:
        items = meli.fetch_most_expensive("MLA352679", 20)
    except Exception as e:
        print(e)
        raise Exception("Items could not be fetched")

    # They should be sorted from the API but just in case
    items.sort(key=lambda item: item["price"], reverse=True)
    return items


def get_vendor_stats() -> list[dict[str, int | str]]:
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

    return [
        {
            "id": item["seller_id"],
            "name": item["seller_name"],
            "total_items": item["total_items"],
            "average_price": item["avg_price"],
            "gold_special": item["gold_special"],
            "gold_pro": item["gold_pro"],
        }
        for item in data
    ]


def fetch_vendor_ids(page: int) -> set[int]:
    return meli.fetch_vendors_from_category("MLA352679", 50, page * 50)


def fetch_vendor_data(vendor_id: int):
    return meli.fetch_vendor_data(vendor_id)
