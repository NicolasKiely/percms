from __future__ import unicode_literals

from django.db import models
from common.core import view_link, edit_link


class Supplier(models.Model):
    ''' Ecommerce Supplier '''
    name = models.CharField('Supplier name', max_length=255)
    description = models.CharField('Supplier description', max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def edit_link(self):
        return edit_link('ecom:supplier_editor', (self.pk,), text='Edit Supplier')

    def view_link(self):
        return view_link('ecom:supplier_view', (self.pk,), text='View Supplier')

    def to_form_fields(self):
        return [
            {'label': 'Name:', 'name': 'name', 'value': self.name},
            {'label': 'Description:', 'name': 'description', 'value': self.description},
            {'type': 'hidden', 'name': 'pk', 'value': self.pk}
        ]
