'''
    Usage:
        python crawler.py

    Will find an inactive crawler instance model, and activate it
'''

import django
import os
import sys
import urllib2

os.environ['DJANGO_SETTINGS_MODULE'] = 'percms.settings'
django.setup()

import crawler.models
from percms import safesettings


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

# Get domain
site = crawler_instance.domain
if site is None:
    print 'Crawler instance is not assigned a website'
    sys.exit(0)

# Get webpage to crawl
path = '/'
webpage = site.domain + path
print 'Processing "%s"' % webpage

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'en-US,en;q=0.8',
    'Accept-Encoding': 'identity',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Referer': webpage,
    'User-Agent': ' '.join([
        'Mozilla/5.0 (X11; Linux x86_64)',
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Ubuntu Chromium/56.0.2924.76',
        'Chrome/56.0.2924.76 Safari/537.36'
    ]),
}
request = urllib2.Request(webpage, None, headers)
response= urllib2.urlopen(request)
html = response.read()

#print html

local_path = safesettings.UPLOAD_CRAWLER_PATH
fh = open(local_path + 'data.html', 'w')
fh.write(html)
fh.close()

print 'done'
