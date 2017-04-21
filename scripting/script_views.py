from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from .models import Script, Source

def get_last_source(script, create_new=False):
    ''' Fetch last source file from script '''
    sources = Source.objects.order_by('-version').filter(script=script)
    if sources.count() > 0:
        # Record found, return last
        return sources[0]
    elif create_new:
        # No record found, create new one
        return Source(script=script, source='', version=0, message='')
    else:
        # No record found, return null
        return None


@login_required
def editor(request, dashboard, pk):
    ''' Script editor '''
    script = get_object_or_404(Script, pk=pk)
    last_source = get_last_source(script, create_new=True)

    context = {
        'code': last_source.source,
        'scriptpk': pk,
        'versions': script.source_set.order_by('-version')
    }
    return dashboard.render_model(request, script, context)


@login_required
def source_editor(request, dashboard, pk):
    ''' Source-specific editor '''
    source = get_object_or_404(Source, pk=pk)
    context = {
        'code': source.source,
        'scriptpk': pk
    }
    return dashboard.render_model(request, source, context)


@login_required
def commit(request):
    ''' Commit code change for a script '''
    fcode = request.POST['code']
    fmsg = request.POST['message']
    fScriptPK = request.POST['scriptpk']

    script = get_object_or_404(Script, pk=fScriptPK)
    sources = Source.objects.filter(script=script)
    if len(sources) == 0:
        # Create first version of script
        v = 0

    else:
        # Append version onto end of list
        v = sources.order_by('-version')[0].version + 1

    new_source = Source(version=v, source=fcode, message=fmsg, script=script)
    new_source.save()
    return HttpResponseRedirect(reverse('script:script_editor', args=(fScriptPK,)))


@login_required
def edit_source(request, dashboard):
    ''' Edit handler for source '''
    source = get_object_or_404(dashboard.model, pk=request.POST['pk'])
    source.message = request.POST['message']
    source.version = int(request.POST['version'])
    source.save()
    return HttpResponseRedirect(reverse('script:script_editor', args=(source.script.pk,)))
