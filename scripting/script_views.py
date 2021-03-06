from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from .models import Script, Source
from django.middleware.csrf import get_token
from . import utils
import traceback

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
        'scriptpk': source.script.pk
    }
    return dashboard.render_model(request, source, context)


@login_required
def commit(request):
    ''' Commit code change for a script '''
    fcode = request.POST['code']
    fmsg = request.POST['message']
    fScriptPK = request.POST['scriptpk']

    script = get_object_or_404(Script, pk=int(fScriptPK))

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


@login_required
def delete_source(request, dashboard):
    ''' Delete handler for source '''
    source = get_object_or_404(dashboard.model, pk=request.POST['pk'])
    scriptpk = source.script.pk
    source.delete()
    return HttpResponseRedirect(reverse('script:script_editor', args=(scriptpk,)))


@login_required
def view_public(request, dashboard, pk):
    ''' View script '''
    obj = get_object_or_404(dashboard.model, pk=pk)
    source = Source.objects.order_by('-version').filter(script=obj)[0]
    context = {
        'panels': [
            {
                'title': 'Test',
                'form': {
                    'action': dashboard.namespace +':test_run',
                    'csrf': get_token(request),
                    'fields': [{'type': 'hidden', 'name': 'pk', 'value': obj.pk}]
                }
            },
            {'title': 'Latest Source', 'pre': source.source}
        ]
    }
    return dashboard.view_model(request, obj, context)


class HTML_Logger_Callback(object):
    def __init__(self): self.results = ''

    def callback(self, msg): self.results += msg + '\n'

log_url = lambda x: reverse('script:logging_view', args=(x.pk,))

@login_required
def test_run(request, dashboard):
    ''' Test run '''
    obj = get_object_or_404(dashboard.model, pk=request.POST['pk'])
    source = Source.objects.order_by('-version').filter(script=obj)[0]
    results = ''
    logger_callback = HTML_Logger_Callback()
    logger = utils.Logging_Runtime('Script_Tester', logger_callback)
    try:
        exec(source.source)
    except Exception as ex:
        logger.log(
            str(type(ex))+' '+str(ex),
            'Exception:\n%s\n\nScript:\n\t%s' %(traceback.format_exc(), str(source))
        )

    context = {
        'panels': [
            {
                'title': 'Test',
                'pre': logger_callback.results,
                'table': {
                    'headers': ['Log Message', 'URL'],
                    'rows': [
                        [str(msg), '<a href="%s">Open</a>' % log_url(msg)]
                        for msg in logger.messages
                    ]
                },
                'form': {
                    'action': dashboard.namespace +':test_run',
                    'csrf': get_token(request),
                    'fields': [{'type': 'hidden', 'name': 'pk', 'value': obj.pk}]
                }
            },
            {'title': 'Latest Source', 'pre': source.source}
        ]
    }
    return dashboard.view_model(request, obj, context)
