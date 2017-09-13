from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Alert(models.Model):
    message = models.CharField('Message to Display', max_length=4096)
    name = models.CharField('Name of alert type', max_length=256)
