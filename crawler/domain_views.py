from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from common import core
from .models import Login_Profile, Website


@login_required
def dashboard(request):
    ''' Top level editor for domains '''
    context = {
        'title': 'Domain Manager',
        'active_websites'  : Website.objects.filter(can_crawl=True)[:5],
        'inactive_websites': Website.objects.filter(can_crawl=False)[:5],
        'form': {
            'action': 'crawler:add_domain',
            'fields': Website().to_form_fields()
        }
    }
    return core.render(request, 'crawler/domain_dashboard.html', **context)


@login_required
def view(request, pk):
    ''' View of domain information '''
    pass


@login_required
def editor(request, pk):
    ''' Editor for domain '''
    pass


@login_required
def add(request):
    ''' Post for adding new domain manually '''
    fdom = request.POST['domain']
    fprof = request.POST['profile']
    fscrap = request.POST['scraper']
    fact = 'cancrawl' in request.POST

    profile = get_object_or_404(Login_Profile, name=fprof)

    website = Website(
        domain=fdom, profile=profile, scraper=fscrap, can_crawl=fact
    )
    website.save()
    return HttpResponseRedirect(reverse('crawler:domain_dashboard'))


@login_required
def edit(request):
    ''' Post for editting existing domain '''
    pass


@login_required
def delete(request):
    ''' Post for deleting domain '''
    pass
