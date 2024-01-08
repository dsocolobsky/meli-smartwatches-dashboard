from typing import Any

import requests

from smartwatches import settings


def fetch_most_expensive(category_id: str, limit: int) -> list[dict[str, str | int]]:
    try:
        response = make_search_request(
            {"category": category_id, "limit": limit, "sort": "price_desc"}
        )
    except Exception as e:
        raise e

    items = [
        {
            "title": item["title"],
            "price": item["price"],
            "permalink": item["permalink"],
            "thumbnail": item.get("thumbnail", None),
        }
        for item in response["results"]
    ]

    return items


def fetch_vendors_from_category(
    category_id: str, pub_limit: int, offset: int = 0
) -> set[int]:
    try:
        response = make_search_request(
            {"category": category_id, "limit": pub_limit, "offset": offset}
        )
    except Exception as e:
        raise e

    items = response["results"]
    vendors = set([item["seller"]["id"] for item in items])
    return vendors


def fetch_vendor_data(vendor_id: int) -> dict[str, int | str]:
    # TODO will have to get all the pages eventually
    try:
        response = make_search_request({"seller_id": vendor_id, "limit": "50"})
    except Exception as e:
        raise e

    data = {
        "seller_id": vendor_id,
        "seller_name": response["seller"]["nickname"],
        "total_items": response["paging"]["total"],
        "gold_special": 0,
        "gold_pro": 0,
    }
    total_price = 0
    for item in response["results"]:
        total_price += item["price"]
        listing_type_id = item.get("listing_type_id", None)
        if listing_type_id == "gold_special":
            data["gold_special"] += 1
        elif listing_type_id == "gold_pro":
            data["gold_pro"] += 1

    data["avg_price"] = total_price / data["total_items"]
    return data


def make_search_request(params: dict[str, Any]):
    try:
        res = requests.get(
            "https://api.mercadolibre.com/sites/MLA/search/", params=params
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(e)
        raise e


def make_oauth_request(code: str) -> dict[str, Any]:
    try:
        res = requests.post(
            "https://api.mercadolibre.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings.MELI_CLIENT_ID,
                "client_secret": settings.MELI_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.MELI_REDIRECT_URI,
            },
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(e)
        raise e


def make_user_request(token: str) -> dict[str, str] | None:
    if not token or len(token) == 0:
        return None
    try:
        res = requests.get(
            "https://api.mercadolibre.com/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        res.raise_for_status()
        json = res.json()
        return {
            "nickname": json["nickname"],
            "first_name": json["first_name"],
            "last_name": json["last_name"],
            "permalink": json["permalink"],
        }
    except Exception as e:
        print(e)
        raise e
