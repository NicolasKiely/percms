from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from common.core import view_link, edit_link
from django.db import models

# Create your models here.
class Alert(models.Model):
    message = models.CharField('Message to Display', max_length=4096)
    name = models.CharField('Name of alert type', max_length=256)

    def __str__(self):
        return self.name

    def edit_link(self):
        return edit_link('alerts:message_editor', (self.pk,))

    def dashboard_link(self):
        url = reverse('alerts:message_dashboard')
        return '<a href="%s">Alert Dashboard</a>' % url

    def to_form_fields(self):
        return [
            {'label': 'Name', 'name': 'name', 'value': self.name},
            {'label': 'Message', 'name': 'message', 'value': self.message},
            {'type': 'hidden', 'name': 'pk', 'value': self.pk}
        ]
