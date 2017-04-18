from __future__ import unicode_literals

from django.db import models

# Languages
langs = (
    ('py', 'Python'),
    ('js', 'Javascript')
)


class Script(models.Model):
    ''' Executable script handle '''
    name = models.CharField('Script Name', max_length=255)
    category = models.CharField('Script Category', max_length=255)
    description = models.CharField('Script Description', max_length=1024)
    lang = models.CharField('Script language', max_length=16, choices=langs)

    def __str__(self):
        return self.category +':'+ self.name


class Source(models.Model):
    ''' Source code for a script '''
    version = models.IntegerField('Version number')
    source = models.TextField('Source code')
    message = models.TextField('Change message')

    def __str__(self):
        return '#'+ str(self.version)
