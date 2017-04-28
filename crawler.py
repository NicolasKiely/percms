'''
    Usage:
        python crawler.py

    Will find an inactive crawler instance model, and activate it
'''

import django
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'percms.settings'
django.setup()

import crawler.models


# Get a crawler 
try:
    crawler_instance = crawler.models.Crawler.objects.get(status='inactive')
except crawler.models.Crawler.DoesNotExist:
    print 'No instances to run'
    sys.exit(0)

print 'done'
