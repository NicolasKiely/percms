from django.contrib.auth.decorators import login_required
from common import core
from .models import Website


@login_required
def dashboard(request):
    ''' Admin dashboard for crawler '''
    context = {
        'title': 'Crawler Dashboard',
        'websites': Website.objects.filter(can_crawl=True)
    }
    return core.render(request, 'crawler/dashboard.html', **context)


@login_required
def public_view(request):
    ''' View of crawler data '''
    context = {
        'title': 'Crawled Data'
    }
    return core.render(request, 'crawler/view.html', **context)
