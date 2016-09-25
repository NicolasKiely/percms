from django.shortcuts import render
from .models import Proj


def editor_list(request):
    ''' Top-levbel editor page for projects '''
    context = {
        'projects': Proj.objects.order_by('-dt_published')
    }
    return core.render(request, 'proj/editor_list.html', **context)
