from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from common import core
from .models import Website
from .dashboard import Dashboard, Website_Dashboard


@login_required
def dashboard(request):
    ''' Admin dashboard for crawler '''
    context = {
        'panels': [
            {
                'title': 'Crawler Status',
                'text': 'Not implemented yet'
            },
            Website_Dashboard.get_dashboard_panel()
        ]
    }
    return Dashboard.render(request, context)


@login_required
def public_view(request):
    ''' View of crawler data '''
    context = {
        'title': 'Crawled Data'
    }
    return core.render(request, 'crawler/view.html', **context)
