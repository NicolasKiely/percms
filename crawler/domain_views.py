from django.contrib.auth.decorators import login_required
from common import core
from .models import Website


@login_required
def dashboard(request):
    ''' Top level editor for domains '''
    context = {
        'title': 'Domain Manager',
        'active_website'  : [Website.objects.filter(can_crawl=True)[0:5]],
        'inactive_website': [Website.objects.filter(can_crawl=False)[0:5]],
        'form': {
            'action': 'crawler:add_domain',
            'fields': Website().to_form_fields()
        }
    }
    return core.render(request, 'crawler/domain_dashboard.html', **context)


@login_required
def editor(request):
    ''' Editor for domain '''
    pass


@login_required
def add(request):
    ''' Post for adding new domain manually '''
    pass


@login_required
def edit(request):
    ''' Post for editting existing domain '''
    pass


@login_required
def delete(request):
    ''' Post for deleting domain '''
    pass
