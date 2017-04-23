from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from common import core
from .models import Login_Profile, Website
from .dashboard import Website_Dashboard


@login_required
def dashboard(request):
    ''' Top level editor for domains '''
    context = {
        'panels': [
            Website_Dashboard.get_listing_panel('Active Domains', can_crawl=True),
            Website_Dashboard.get_listing_panel('Inactive Domains', can_crawl=False)
        ]
    }
    return Website_Dashboard.render_model_set(request, context)


@login_required
def view(request, pk):
    ''' View of domain information '''
    pass


@login_required
def editor(request, pk):
    ''' Editor for domain '''
    website = get_object_or_404(Website, pk=pk)
    return Website_Dashboard.render_model(request, website, {})


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
    p = request.POST
    website = get_object_or_404(Website, pk=p['pk'])
    profile_name = p['profile']
    if profile_name:
        profile = get_object_or_404(Login_Profile, name=p['profile'])
    else:
        profile = None
    website.domain = p['domain']
    website.can_crawl = 'cancrawl' in p
    website.profile = profile
    website.scraper = p['scraper']
    website.save()

    return HttpResponseRedirect(reverse('crawler:domain_dashboard'))


@login_required
def delete(request):
    ''' Post for deleting domain '''
    website = get_object_or_404(Website, pk=request.POST['pk'])
    website.delete()

    return HttpResponseRedirect(reverse('crawler:domain_dashboard'))
