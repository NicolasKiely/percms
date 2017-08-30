from . import models
from crawler.models import Webpage


def price_to_cents(pstr):
    ''' Converts price to integer of cents '''
    price_string = pstr.lstrip('$').replace(',', '')
    dollar, cents = price_string.split('.')
    return int(dollar) * 100 + int(cents)

def add_product(supplier_name, prod_data):
    ''' Helper function for importing product data from scripts '''
    supplier = models.Supplier.objects.get(name=supplier_name)
    prod = models.Product.objects.get_or_create(
        supplier=supplier, name=prod_data['name']
    )[0]
    prod.description = prod_data.get('description', '')
    prod.inventory = int(prod_data.get('inventory', 0))
    prod.price_cents = price_to_cents(prod_data['price'])

    if 'webpage.id' in prod_data:
        prod.webpage = Webpage.objects.get(pk=prod_data['webpage.id'])
    prod.save()
