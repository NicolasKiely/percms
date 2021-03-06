from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
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
        return edit_link('script:script_editor', (self.pk,), text='Edit Script')

    def view_link(self):
        return view_link('script:script_view', (self.pk,), text='View Script')

    def dashboard_link(self):
        url = reverse('script:script_dashboard')
        return '<a href="'+ url +'">Script Dashboard</a>'

    def nav_link(self):
        return self.dashboard_link() +' | '+ self.view_link()

    def get_latest_source(self):
        return Source.objects.order_by('-version').filter(script=self)[0]

    def to_form_fields(self):
        return [
            {'label': 'Name:', 'name': 'name', 'value': self.name},
            {'label': 'Category', 'name': 'category', 'value': self.category},
            {'label': 'Description', 'name': 'description', 'value': self.description},
            {
                'type': 'select', 'label': 'Language',
                'name': 'lang', 'value': self.lang,
                'options': langs
            },
            {'type': 'hidden', 'name': 'pk', 'value': self.pk}
        ]


class Source(models.Model):
    ''' Source code for a script '''
    version = models.IntegerField('Version number')
    source = models.TextField('Source code')
    message = models.TextField('Change message')
    script = models.ForeignKey(Script, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.script) +'#'+ str(self.version)

    def short_message(self):
        return self.message[:20]

    def edit_link(self):
        return edit_link('script:source_editor', (self.pk,), text='Edit Version')

    def view_link(self):
        return view_link('script:source_view', (self.pk,), text='View Version')

    def nav_link(self):
        return self.script.edit_link() +' | '+ self.view_link()

    def to_form_fields(self):
        return [
            {'label': 'Message: ', 'name': 'message', 'value': self.message},
            {'label': 'Version: ', 'name': 'version', 'value': self.version},
            {'type': 'hidden', 'name': 'pk', 'value': self.pk}
        ]


class Log_Message(models.Model):
    ''' Simple logging system to be used for apps using scripting system '''
    stamp = models.DateTimeField('Start date of contigous data pulled')
    app_name = models.TextField('Name of app to register message')
    short_message = models.TextField('Short description of message')
    long_message = models.TextField('Long description of message')

    def __str__(self):
        return '[%s] %s: %s' % (self.stamp, self.app_name, self.short_message)

    def to_form_fields(self):
        return [
            {'label': 'App Name', 'name': 'app', 'value': self.app_name},
            {'label': 'Short Message', 'name': 'short', 'value': self.short_message},
            {'label': 'Long Message', 'name': 'long', 'value': self.long_message},
        ]
