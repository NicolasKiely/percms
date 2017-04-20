from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from .models import Script



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
