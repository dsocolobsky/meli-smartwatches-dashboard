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