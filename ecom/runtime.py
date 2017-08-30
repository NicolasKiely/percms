from django.utils import timezone

from . import models
from percms import safesettings
from crawler.models import Webpage
from filemanager.models import Meta_File
import urllib2


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

    # Save images
    for image in prod_data.get('images', []):
        save_product_image(supplier_name, prod, image)

    prod.save()

    return prod


def save_product_image(supplier_name, product, image_url):
    ''' Saves image and returns object '''
    # Create metadata entry
    img_name = image_url.replace('/', '-')
    img_cat = supplier_name.replace(' ', '-') + '-image'
    try:
        meta_file = Meta_File.objects.get(name=img_name, category=img_cat)
    except Meta_File.DoesNotExist:
        meta_file = Meta_File(
            name=img_name,
            category=img_cat,
            dt_uploaded = timezone.now(),
            is_img=True
        )
        meta_file.save()
    sid = str(meta_file.id)
    save_path = safesettings.UPLOAD_IMAGE_PATH + sid

    # Download image
    request = urllib2.Request(image_url)
    image_source = urllib2.urlopen(request)

    # Save to file
    with open(save_path, 'wb+') as dest:
        dest.write(image_source.read())

    product.save()
    product.images.add(meta_file)
