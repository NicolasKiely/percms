from django.shortcuts import render
from django.http import HttpResponse
from common import core
#from login import forms

home_panels = {
    'title': 'About',
    'components': [
        {
            'type' : 'text',
            'model': 'raw',
            'src'  : 'Welcome to my portfolio website'
        }
    ]
}

def index(request):
    context = {
        'panels': [ home_panels ]
    }
    return core.render(request, 'common/docpage.html', **context)
