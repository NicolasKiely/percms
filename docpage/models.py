from django.db import models
from django.core.urlresolvers import reverse

# Component model choices
mchoices = (
    ('raw', 'Raw text'),
    ('sapi', 'Static API'),
    ('dapi', 'Dynamic API'),
    ('mu', 'Markup text')
)

# Components view choices
vchoices = (
    ('text', 'Text'),
    ('img', 'Image'),
    ('table', 'Table')
)

class DocPage(models.Model):
    ''' Generic multi-component page '''
    #name = models.CharField("Page URL Title", max_length=32)
    title = models.CharField("Page Title", max_length=255)
    category = models.CharField('Page Category', max_length=255, default='home')
    dt_published = models.DateTimeField('Data Published')
    dt_editted = models.DateTimeField('Date Last Editted')

    def get_view_url(self):
        ''' Returns view url '''
        url = reverse('docpage:view_page', args=(self.id,)) 
        return url + self.get_normalized_name()

    def get_normalized_name(self):
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

    def __unicode__(self):
        return self.category +':'+ self.get_normalized_name()


class Panel(models.Model):
    ''' Stylistic panel on a page '''
    title = models.CharField('Panel Header', max_length=255, default='')
    page = models.ForeignKey(DocPage, on_delete=models.CASCADE)


class Component(models.Model):
    ''' Display object in a panel '''
    src   = models.CharField("Data Source", max_length=4096)
    model = models.CharField('Model type', max_length=64, choices=mchoices)
    view  = models.CharField('View type', max_length=64, choices=vchoices)
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE)
