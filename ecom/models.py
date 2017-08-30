from __future__ import unicode_literals

from django.db import models

from common.core import view_link, edit_link
from crawler.models import Website, Webpage


class Supplier(models.Model):
    ''' Ecommerce Supplier '''
    name = models.CharField('Supplier name', max_length=255, unique=True)
    description = models.CharField('Supplier description', max_length=255)
    active = models.BooleanField(default=True)
    website = models.ForeignKey(Website, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    def edit_link(self):
        return edit_link('ecom:supplier_editor', (self.pk,), text='Edit Supplier')

    def view_link(self):
        return view_link('ecom:supplier_view', (self.pk,), text='View Supplier')

    def nav_link(self):
        return self.view_link()

    def to_form_fields(self):
        domain = 'http://' if self.website is None else self.website.domain
        return [
            {'label': 'Name:', 'name': 'name', 'value': self.name},
            {'label': 'Description:', 'name': 'description', 'value': self.description},
            {'label': 'Website', 'name': 'website', 'value': domain},
            {'type': 'hidden', 'name': 'pk', 'value': self.pk}
        ]


class Product(models.Model):
    ''' Product from ecommerce supplier '''
    name = models.CharField('Supplier name', max_length=255)
    description = models.CharField('Supplier description', max_length=4096)
    staged = models.BooleanField(default=False)
    blacklist = models.BooleanField(default=False)
    inventory = models.IntegerField(default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    webpage = models.ForeignKey(Webpage, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def edit_link(self):
        return edit_link('ecom:product_editor', (self.pk,), text='Edit Product')

    def view_link(self):
        return view_link('ecom:product_view', (self.pk,), text='View Product')

    def nav_link(self):
        return self.view_link()

    def to_form_fields(self, field=None, fk=None):
        supplier = {'name': 'supplier'}
        if self.supplier:
            supplier['label'] = 'Supplier:'
            supplier['value'] = self.supplier.name

        elif field=='supplier':
            supplier['type'] = 'hidden'
            supplier['value'] = Supplier.objects.get(pk=fk).name

        else:
            supplier['label'] = 'Supplier:'
            supplier['value'] = ''

        return [
            {'label': 'Name:', 'name': 'name', 'value': self.name},
            {'label': 'Description:', 'name': 'description', 'value': self.description},
            {'label': 'Count:', 'name': 'inventory', 'value': self.inventory},
            supplier,
            {'type': 'hidden', 'name': 'pk', 'value': self.pk}
        ]
