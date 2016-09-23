from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Proj(models.Model):
    ''' Project Information '''
    title = models.CharField("Project Title", max_length=255)
    category = models.CharField("Project Category", max_length=255)
    dt_published = models.DateTimeField('Date Published')
