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

# Get configuration
crawler_config = crawler_instance.config
if crawler_config is None:
    print 'Crawler instance is not assigned a configuration'
    sys.exit(0)

# Get active state
crawler_state = crawler_instance.active_state
if crawler_state is None:
    crawler_state = crawler_config.initial_state
    if crawler_state is None:
        print 'Configuration "%s" has no preset state' % crawler_config.name
        sys.exit(0)

print 'Using crawler configuration "%s:%s"' % (crawler_config.name, crawler_state.name)

print 'done'
