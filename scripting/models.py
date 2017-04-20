from __future__ import unicode_literals

from django.db import models
from common.core import view_link, edit_link

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

    def edit_link(self):
        return edit_link('script:script_editor', (self.pk,))

    def view_link(self):
        return view_link('script:script_view', (self.pk,))

    def to_form_fields(self):
        return [
            {'label': 'Name:', 'name': 'name', 'value': self.name},
            {'label': 'Category', 'name': 'category', 'value': self.category},
            {'label': 'Description', 'name': 'description', 'value': self.description},
            {
                'type': 'select', 'label': 'Language',
                'name': 'lang', 'value': self.lang,
                'options': langs
            }
        ]


class Source(models.Model):
    ''' Source code for a script '''
    version = models.IntegerField('Version number')
    source = models.TextField('Source code')
    message = models.TextField('Change message')
    script = models.ForeignKey(Script, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return '#'+ str(self.version)
