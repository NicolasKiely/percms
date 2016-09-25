from django.shortcuts import render
from common import core
from .models import Proj


def editor_list(request):
    ''' Top-levbel editor page for projects '''
    context = {
        'projects': Proj.objects.order_by('-dt_published')
    }
    return core.render(request, 'proj/editor_list.html', **context)


def editor(request, pk):
    ''' Editor for a project '''


def edit(request):
    ''' Post handle for editting a project '''


def add(request):
    ''' Post handle for adding a new project '''


def view(request, pk):
    ''' Displays project '''
