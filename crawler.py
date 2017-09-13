''' Main Crawler Script
    Usage:
        python crawler.py

    Will find an inactive crawler instance model, and activate it
    Flow:
        For a given state, get list of webpage vist requests
        If a request exists:
            Download page
            Call state script on page data
        Else:
            If on initial state:
                Get home page of domain
                Call state script on page data

            If next state given
                Go to next state
            Else
                Go to initial state
'''

import django
import os
import sys
import urllib2

os.environ['DJANGO_SETTINGS_MODULE'] = 'percms.settings'
django.setup()

import crawler.models
from percms import safesettings


def state_has_active_markers(crawler_state):
    ''' Returns true if crawler state has active pages to crawl '''
    markers = crawler.models.Webpage_Mark.objects.filter(
        state=crawler_state, to_crawl=True
    )
    return len(markers) > 0


def revert_crawler(crawler_instance):
    ''' Revers crawler to initial state, and returns state '''
    crawler_instance.active_state = crawler_instance.config.initial_state
    if crawler_instance.active_state is None:
        print 'Configuration "%s" has no preset state' % (
            str(crawler_instance.config),
        )
        sys.exit(0)

    # Re-Mark home page
    home_page, x = crawler.models.Webpage.objects.get_or_create(
        website=crawler_instance.domain, path='/'
    )

    home_mark, x = crawler.models.Webpage_Mark.objects.get_or_create(
        state=crawler_instance.active_state, webpage=home_page
    )
    home_mark.to_crawl = True
    home_mark.save()


def get_active_state(crawler):
    ''' Loads active state of crawler; sets to initial state if null '''
    if crawler.active_state is None:
        # Default to initial state
        revert_crawler(crawler)

    else:
        # Return active state with markers left
        while not state_has_active_markers(crawler.active_state):
            # Nothing to crawl on this state, skip
            print 'Skiping state '+str(crawler.active_state)

            crawler.active_state = crawler.active_state.next_state

            if crawler.active_state is None:
                revert_crawler(crawler)
                break

    crawler.save()
    return crawler.active_state


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
crawler_state = get_active_state(crawler_instance)
print 'Using crawler configuration "%s:%s"' % (crawler_config.name, crawler_state.name)

# Get domain
site = crawler_instance.domain
if site is None:
    print 'Crawler instance is not assigned a website'
    sys.exit(0)

# Get webpage to crawl
if crawler_state.id == crawler_config.initial_state.id:
    # Initial state; use index page
    path = '/'
    try:
        webpage = crawler.models.Webpage.objects.get(website=site, path=path)
    except crawler.models.Webpage.DoesNotExist:
        webpage = crawler.models.Webpage(website=site, path=path)
        webpage.save()

    try:
        marker = crawler.models.Webpage_Mark.objects.get(
            state=crawler_state, to_crawl=True, webpage=webpage
        )
    except crawler.models.Webpage_Mark.DoesNotExist:
        marker = crawler.models.Webpage_Mark(
            state=crawler_state, to_crawl=True, webpage=webpage
        )
        marker.save()

else:
    # Get marker for this state
    marker = crawler.models.Webpage_Mark.objects.filter(
        state=crawler_state, to_crawl=True
    )[0]

    webpage = marker.webpage
    path = webpage.path


url = site.domain + path
print 'Processing "%s"' % url


# HTTP request
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'en-US,en;q=0.8',
    'Accept-Encoding': 'identity',
    'Referer': url,
    'User-Agent': ' '.join([
        'Mozilla/5.0 (X11; Linux x86_64)',
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Ubuntu Chromium/56.0.2924.76',
        'Chrome/56.0.2924.76 Safari/537.36'
    ]),
}
if crawler_instance.cookies:
    headers['cookie'] = crawler_instance.cookies

request = urllib2.Request(url, None, headers)
response= urllib2.urlopen(request)
html = response.read()

# Fetch page
local_path = safesettings.UPLOAD_CRAWLER_PATH
fh = open('%spage-%s.html' % (local_path, str(webpage.pk)), 'w')
fh.write(html.encode('utf-8', 'ignore'))
fh.close()

# Apply code
execl_args = [
    'python',
    'python',
    'script_executor.py',
    str(crawler_state.get_source()),
    'domain='+ site.domain,
    'path='+ path,
    'marker.id='+ str(marker.pk),
    'webpage.id='+ str(webpage.pk),
    'crawler.id='+ str(crawler_instance.pk)
]
print ' '.join(execl_args)

# TODO: Fork script executor and pipe I/O to manage it
marker.to_crawl = False
marker.save()
os.execlp(*execl_args)
