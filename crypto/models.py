from __future__ import unicode_literals

from django.db import models
from common.core import view_link, edit_link

# Create your models here.
class API_Key(models.Model):
    name = models.CharField('Name of Key', max_length=256)
    key = models.CharField('Key', max_length=4096)
    secret = models.CharField('Key secret', max_length=4096)

    def __str__(self):
        return self.name
