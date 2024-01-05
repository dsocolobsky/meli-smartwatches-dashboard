import django
import requests
from django.shortcuts import render

class HomeView(django.views.View):

    def get(self, request):
        meli_response = requests.get('https://api.mercadolibre.com/sites/MLA/search/',
                         params={'category': 'MLA352679', 'limit': '10', 'sort': 'price_desc'}).json()

        print(meli_response)
        items = [{'title': item['title'], 'price': item['price'], 'permalink': item['permalink']}
                 for item in meli_response['results']]

        print(items)

        return render(request, 'mas_caros.html', {'items': items})


class SellerStatsView(django.views.View):

    def get(self, request):
        # Get the first 1000 items from the Smartwatch category
        meli_response = requests.get('https://api.mercadolibre.com/sites/MLA/search/',
                         params={'category': 'MLA352679', 'limit': '50'}).json()
        items = meli_response['results']
        print(f"Total items: {len(items)}")
        sellers = set([item['seller']['id'] for item in items][:4])

        data = []
        for seller in sellers:
            print(f"Getting data for seller {seller}")
            data.append(self.data_for_seller(seller))
        # Sort by total items desc
        data.sort(key=lambda x: x['total_items'], reverse=True)

        return render(request, 'vendedores.html', {'sellers': data})

    def data_for_seller(self, seller):
        data = {}
        meli_response = requests.get('https://api.mercadolibre.com/sites/MLA/search/',
                                     params={'seller_id': seller, 'limit': '50'}).json()

        data['seller_id'] = seller
        data['seller_name'] = meli_response['seller']['nickname']
        data['total_items'] = meli_response['paging']['total']
        data['gold_special'] = 0
        data['gold_pro'] = 0
        total_price = 0
        for item in meli_response['results']:
            print(item)
            total_price += item['price']
            listing_type_id = item.get('listing_type_id', None)
            if listing_type_id == 'gold_special':
                data['gold_special'] += 1
            elif listing_type_id == 'gold_pro':
                data['gold_pro'] += 1

        data['avg_price'] = total_price / data['total_items']
        return data
