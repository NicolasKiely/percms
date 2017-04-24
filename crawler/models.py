from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from common.core import view_link, edit_link
from scripting.models import Source


statuses = (
    ('running', 'Running'),   # Currently running
    ('paused', 'Paused'),     # Paused by user
    ('stopped', 'Stopped'),   # Stopped due to some condition
    ('finished', 'Finished')  # Finished with no work left to do
)


class Login_Profile(models.Model):
    ''' Login profile for websites '''
    name     = models.CharField(max_length=64, unique=True)
    username = models.CharField(max_length=64, default='Percms Bot')
    email    = models.CharField(max_length=64, default='')
    password = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Website(models.Model):
    ''' Website domain '''
    domain = models.CharField(max_length=255, unique=True)

    # If crawlable
    can_crawl = models.BooleanField(default=False)

    # Login profile
    profile = models.ForeignKey(
        Login_Profile, on_delete=models.SET_NULL, null=True
    )

    # Last visit
    last_visit = models.DateTimeField(null=True)

    # Scraper module
    scraper = models.CharField(max_length=32, null=True)

    def __str__(self):
        return self.domain

    def edit_link(self):
        return edit_link('crawler:domain_editor', (self.pk,))

    def view_link(self):
        return view_link('crawler:domain_view', (self.pk,), self.domain)

    def dashboard_link(self):
        url = reverse('crawler:domain_dashboard')
        return '<a href="'+ url +'">Domain Dashboard</a>'

    def nav_link(self):
        return self.dashboard_link() +' | '+ self.view_link()

    def to_form_fields(self):
        return [
            {'label': 'Domain:'   , 'name': 'domain'   , 'value': self.domain},
            {
                'type': 'select', 'label': 'Profile',
                'name': 'profile', 'value': self.get_profile_name(),
                'options': [''] + [map(str, Login_Profile.objects.all())]
            },
            {
                'type': 'text', 'label': 'Scraper', 
                'name': 'scraper', 'value': self.scraper
            },
            {
                'type': 'checkbox', 'label': 'Crawling:' ,
                'name': 'cancrawl', 'value': self.can_crawl
            },
            { 'type': 'hidden', 'name': 'pk', 'value': self.pk }
        ]

    def get_profile_name(self):
        return self.profile.name if self.profile else ''
 

class Crawler_Config(models.Model):
    ''' Crawler config and state '''
    # Name of config
    name = models.CharField(max_length=64, unique=True)

    # Initial/default state
    initial_state = models.ForeignKey('Crawler_State', on_delete=models.SET_NULL, null=True)


class Crawler_State(models.Model):
    ''' Sequential State of crawler '''
    # Name of state
    name = models.CharField(max_length=64)

    # Config this state belongs to
    config = models.ForeignKey(Crawler_Config, on_delete=models.CASCADE)

    # Source code to execute on state visit
    source = models.ForeignKey(Source, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'config')


class Crawler(models.Model):
    ''' Running/Sleeping instance of crawler '''
    # Domain to run on
    domain = models.ForeignKey(Website, on_delete=models.SET_NULL, null=True)

    # Configuration of crawler
    config = models.ForeignKey(Crawler_Config, on_delete=models.SET_NULL, null=True)

    # Active State of crawler
    active_state = models.ForeignKey(Crawler_State, on_delete=models.SET_NULL, null=True)

    # Sleep time between page visits
    wait_time = models.IntegerField(default=0)

    # Crawler status
    status = models.CharField(max_length=64, choices=statuses)


    def get_domain(self):
        return self.domain.domain if self.domain else ''

    def get_config(self):
        return self.config.name if self.config else ''

    def get_state(self):
        return self.state.name if self.state else ''
