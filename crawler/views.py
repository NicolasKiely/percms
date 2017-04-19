from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from common import core
from .models import Website


@login_required
def dashboard(request):
    ''' Admin dashboard for crawler '''
    context = {
        'title': 'Crawler Dashboard',
        'app': 'Crawler',

        'panels': [
            {
                'title': 'Crawler Status',
                'text': 'Not implemented yet'
            },
            {
                'title': 'Domain Management',
                'link': reverse('crawler:domain_dashboard'),
                'table': {
                    'headers': ['Domain', 'Module', 'Login Profile'],
                    'rows': [
                        (w.domain, w.scraper, w.profile.name)
                        for w in Website.objects.filter(can_crawl=True)
                    ]
                }
            }
        ],
        'websites': Website.objects.filter(can_crawl=True)
    }
    return core.render(request, 'common/app_dashboard.html', **context)


@login_required
def public_view(request):
    ''' View of crawler data '''
    context = {
        'title': 'Crawled Data'
    }
    return core.render(request, 'crawler/view.html', **context)
