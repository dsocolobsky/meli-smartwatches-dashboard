import requests


class MeliService:

    def fetch_most_expensives(self, category_id, limit):
        try:
            meli_response = self.make_request({'category': category_id, 'limit': limit, 'sort': 'price_desc'})
        except Exception as e:
            raise e

        items = [{'title': item['title'], 'price': item['price'], 'permalink': item['permalink']}
                 for item in meli_response['results']]

        return items

    def fetch_vendors_from_category(self, category_id, pub_limit):
        try:
            meli_response = self.make_request({'category': category_id, 'limit': pub_limit})
        except Exception as e:
            raise e

        items = meli_response['results']
        sellers = set([item['seller']['id'] for item in items][:4])
        return sellers

    def fetch_vendor_data(self, vendor_id):
        try:
            meli_response = self.make_request({'seller_id': vendor_id, 'limit': '50'})
        except Exception as e:
            raise e

        data = {'seller_id': vendor_id, 'seller_name': meli_response['seller']['nickname'],
                'total_items': meli_response['paging']['total'], 'gold_special': 0, 'gold_pro': 0}
        total_price = 0
        for item in meli_response['results']:
            total_price += item['price']
            listing_type_id = item.get('listing_type_id', None)
            if listing_type_id == 'gold_special':
                data['gold_special'] += 1
            elif listing_type_id == 'gold_pro':
                data['gold_pro'] += 1

        data['avg_price'] = total_price / data['total_items']
        return data

    def make_request(self, params):
        # TODO log the actual error
        try:
            res = requests.get('https://api.mercadolibre.com/sites/MLA/search/', params=params)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            print(e)
            raise e

