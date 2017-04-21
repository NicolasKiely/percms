from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from .models import Script, Source

def get_last_source(:q

@login_required
def editor(request, dashboard, pk):
    obj = get_object_or_404(Script, pk=pk)

    context = {
        'code': 'def foo(a, b):\n    return a+b\nprint "<foo>:"+str(foo(5, 7))',
        'scriptpk': pk,
        'versions': obj.source_set.order_by('-version')
    }
    return dashboard.render_model(request, obj, context)


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
