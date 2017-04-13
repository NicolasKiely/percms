from __future__ import unicode_literals

from django.db import models


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
    domain = models.CharField(max_length=255)

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
