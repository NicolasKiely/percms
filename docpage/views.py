from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from common import core


@login_required
def editor(request):
    ''' Top-level editor page for docs '''
    context = {
    }
    return core.render(request, 'docpage/editor_list.html', *context)
