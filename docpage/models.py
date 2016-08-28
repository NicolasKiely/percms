from django.db import models


class ModelType(models.Model):
    ''' Types of a component's data model '''
    name = models.CharField('Model type name', max_length=64)
    def __unicode__(self): return unicode(self.name)


class ViewType(models.Model):
    ''' Types of a component's view '''
    name = models.CharField('View type name', max_length=64)
    def __unicode__(self): return unicode(self.name)


class DocPage(models.Model):
    ''' Generic multi-component page '''
    title = models.CharField("Page Title", max_length=255)


class Panel(models.Model):
    ''' Stylistic panel on a page '''
    page = models.ForeignKey(DocPage, on_delete=models.CASCADE)


class Component(models.Model):
    ''' Display object in a panel '''
    src   = models.CharField("Data Source", max_length=4096)
    model = models.ForeignKey(ModelType)
    view  = models.ForeignKey(ViewType)
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE)
