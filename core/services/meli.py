import requests


def meli_fetch_most_expensive(category_id, limit):
    try:
        meli_response = meli_make_search_request(
            {"category": category_id, "limit": limit, "sort": "price_desc"}
        )
    except Exception as e:
        raise e

    items = [
        {
            "title": item["title"],
            "price": item["price"],
            "permalink": item["permalink"],
        }
        for item in meli_response["results"]
    ]

    return items


def meli_fetch_vendors_from_category(category_id, pub_limit):
    try:
        meli_response = meli_make_search_request(
            {"category": category_id, "limit": pub_limit}
        )
    except Exception as e:
        raise e

    items = meli_response["results"]
    sellers = set([item["seller"]["id"] for item in items][:4])
    return sellers


def meli_fetch_vendor_data(vendor_id):
    # TODO will have to get all the pages eventually
    try:
        meli_response = meli_make_search_request(
            {"seller_id": vendor_id, "limit": "50"}
        )
    except Exception as e:
        raise e

    data = {
        "seller_id": vendor_id,
        "seller_name": meli_response["seller"]["nickname"],
        "total_items": meli_response["paging"]["total"],
        "gold_special": 0,
        "gold_pro": 0,
    }
    total_price = 0
    for item in meli_response["results"]:
        total_price += item["price"]
        listing_type_id = item.get("listing_type_id", None)
        if listing_type_id == "gold_special":
            data["gold_special"] += 1
        elif listing_type_id == "gold_pro":
            data["gold_pro"] += 1

    data["avg_price"] = total_price / data["total_items"]
    return data


def meli_make_code_request():
    # TODO log the actual error
    try:
        res = requests.get(
            "https://auth.mercadolibre.com.ar/authorization",
            params={
                "response_type": "code",
                "client_id": "3653090375391988",
                "redirect_uri": "https://localhost:8000/token",
            },
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(e)
        raise e


def meli_make_search_request(params):
    # TODO log the actual error
    try:
        res = requests.get(
            "https://api.mercadolibre.com/sites/MLA/search/", params=params
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(e)
        raise e


def meli_make_oauth_request(code):
    # TODO log the actual error
    try:
        res = requests.post(
            "https://api.mercadolibre.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": "3653090375391988",
                "client_secret": "L1Y1l0QO1bcoq7KOXVyAZoZrzoEhCjQG",
                "code": code,
                "redirect_uri": "https://localhost:8000/token",
            },
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(e)
        raise e


def meli_make_user_request(token):
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
