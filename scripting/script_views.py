from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from .models import Script


def view(request):
    pass


@login_required
def editor(request, dashboard, pk):
    obj = get_object_or_404(Script, pk=pk)
    context = {
        'panels': [
            {
                'title': 'Code'
            },
            {
                'title': 'Version History'
            }
        ]
    }
    return dashboard.render_model(request, obj, context)


@login_required
def add(request):
    fname = request.POST['name']
    fcat = request.POST['category']
    fdesc = request.POST['description']
    flang = request.POST['lang']

    script = Script(
        name=fname, category=fcat, description=fdesc, lang=flang
    )
    script.save()
    return HttpResponseRedirect(reverse('script:script_dashboard'))

@login_required
def edit(request):
    script = get_object_or_404(Script, pk=request.POST['pk'])
    script.name = request.POST['name']
    script.category = request.POST['category']
    script.description = request.POST['description']
    script.lang = request.POST['lang']

    script.save()
    return HttpResponseRedirect(reverse('script:script_dashboard'))
