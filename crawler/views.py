from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from common import core
from . import models
from scripting.models import Source, Script



@login_required
def public_view(request):
    ''' View of crawler data '''
    context = {
        'title': 'Crawled Data'
    }
    return core.render(request, 'crawler/view.html', **context)


@login_required
def add_crawler(request, dashboard):
    ''' Add new crawler instance '''
    p = request.POST
    fdomain = p['domain']
    fconfig = p['config']

    if fdomain:
        domain = get_object_or_404(models.Website, domain=fdomain)
    else:
        domain = None

    if fconfig:
        config = get_object_or_404(models.Crawler_Config, name=fconfig)
    else:
        config = None

    crawler = models.Crawler(domain=domain, config=config)
    crawler.save()

    return HttpResponseRedirect(dashboard.reverse_dashboard())


@login_required
def edit_crawler(request, dashboard):
    ''' Edit crawler instance '''
    p = request.POST
    fdomain = p['domain']
    fconfig = p['config']
    fstatus = p['status']

    if fdomain:
        domain = models.Website.objects.get(domain=fdomain)
    else:
        domain = None

    if fconfig:
        config = get_object_or_404(models.Crawler_Config, name=fconfig)
    else:
        config = None

    crawler = get_object_or_404(models.Crawler, pk=p['pk'])
    crawler.domain = domain
    crawler.config = config
    crawler.status = fstatus.lower()
    crawler.save()
    return HttpResponseRedirect(dashboard.reverse_dashboard())


@login_required
def add_config(request, dashboard):
    ''' Add new crawler configuration '''
    p = request.POST
    fname = p['name']
    crawler_config = models.Crawler_Config(name=fname)
    crawler_config.save()

    return HttpResponseRedirect(dashboard.reverse_dashboard())


@login_required
def edit_config(request, dashboard):
    ''' Edit crawler configuration '''
    p = request.POST
    fname = p['name']
    fstate = p['initial_state']

    crawler_config = get_object_or_404(models.Crawler_Config, pk=p['pk'])
    crawler_config.name = fname
    
    if fstate:
        istate = get_object_or_404(
            models.Crawler_State, config=crawler_config, name=fstate
        )
        crawler_config.initial_state = istate
    crawler_config.save()

    return HttpResponseRedirect(dashboard.reverse_dashboard())


@login_required
def add_state(request, dashboard):
    ''' Add new config state '''
    p = request.POST
    config = models.Crawler_Config.objects.get(name=p['config'])
    fname = p['name']
    fnext = p['next']
    script_cat, script_post = p['source'].split(':', 1)
    script_name, script_version = script_post.split('#', 1)
    script = Script.objects.get(category=script_cat, name=script_name)
    source = Source.objects.get(version=script_version, script=script)
    if fnext == '':
        next_state = None
    else:
        next_state = models.Crawler_State.objects.get(config=config, name=fnext)

    state = models.Crawler_State(
        name=fname,
        config=config,
        source=source,
        next_state=next_state
    )
    state.save()

    parent_dash = dashboard.get_parent('config')
    return HttpResponseRedirect(parent_dash.reverse_editor(config.id))


@login_required
def edit_state(request, dashboard):
    ''' Edit config state '''
    p = request.POST
    config = models.Crawler_Config.objects.get(name=p['config'])
    fname = p['name']
    fnext = p['next']
    script_cat, script_post = p['source'].split(':', 1)
    script_name, script_version = script_post.split('#', 1)
    script = get_object_or_404(Script, category=script_cat, name=script_name)
    source = get_object_or_404(Source, version=script_version, script=script)
    if fnext == '':
        next_state = None
    else:
        next_state = models.Crawler_State.objects.get(config=config, name=fnext)

    state = get_object_or_404(models.Crawler_State, pk=p['pk'])
    state.name = fname
    state.source = source
    state.next_state = next_state
    state.save()

    parent_dash = dashboard.get_parent('config')
    return HttpResponseRedirect(parent_dash.reverse_editor(config.id))
