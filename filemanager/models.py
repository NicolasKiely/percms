from __future__ import unicode_literals

from django.db import models


class Meta_File(models.Model):
    ''' Stores meta-information about uploaded files '''
    name = models.CharField('File Name', max_length=255)
    category = models.CharField('File Category', max_length=255, default='')
    # Note: For purposes of storage, images are treated separately
    is_img = models.BooleanField('Is File an Image')
    dt_uploaded = models.DateTimeField('Date Uploaded')

    def __unicode__(self):
        return self.category +':'+ self.name

