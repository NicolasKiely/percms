from __future__ import unicode_literals

from django.db import models
from percms import safesettings
from django.core.urlresolvers import reverse


class Meta_File(models.Model):
    ''' Stores meta-information about uploaded files '''
    name = models.CharField('File Name', max_length=255)
    category = models.CharField('File Category', max_length=255, default='')
    # Note: For purposes of storage, images are treated separately
    is_img = models.BooleanField('Is File an Image')
    dt_uploaded = models.DateTimeField('Date Uploaded')

    def get_url_path(self):
        sid = str(self.id)
        if self.is_img:
            return '/static/images/%s'% sid
        else:
            return '/static/files/%s'% sid

    def get_download_url(self):
        return reverse('file:download', args=(self.pk,))
        

    def get_file_path(self):
        sid = str(self.id)
        if self.is_img:
            save_path = safesettings.UPLOAD_IMAGE_PATH + sid
        else:
            save_path = safesettings.UPLOAD_FILE_PATH + sid
        return save_path

    def __unicode__(self):
        return self.category +':'+ self.name

