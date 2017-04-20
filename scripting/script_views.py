from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from .models import Script


def view(request):
    pass


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

def edit(request):
    pass

def delete(request):
    pass
