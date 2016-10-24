from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models

# Create your models here.


class Proj(models.Model):
    ''' Project Information '''
    title = models.CharField("Project Title", max_length=255)
    category = models.CharField("Project Category", max_length=255)
    dt_published = models.DateTimeField('Date Published')

    def get_normalize_name(self):
        ''' Returns url-friendly normalized name '''
        underscore = False
        normalized = ''
        for c in self.title.lower():
            if 'a'<=c<='z' or '0'<=c<='9':
                normalized += c
                underscore = True
            elif underscore:
                normalized += '_'
                underscore = False
            if len(normalized) >= 32: break
        return normalized


    def get_view_url(self):
        ''' Returns view url '''
        url = reverse('project:view', args=(self.id,))
        return url + self.get_normalize_name()


    def get_view_link(self, title=None):
        ''' Returns link to view '''
        title = title if title else self.title
        return '<a href="'+ self.get_view_url() +'">'+ title +'</a>'
