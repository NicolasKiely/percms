from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from common import core
from docpage.models import DocPage
import docpage.views
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
    ''' Shows site homepage as the docpage "site:index", or default page '''
    try:
        # Try to load site:index
        index_page = DocPage.objects.get(category='site', title='index')
        return docpage.views.render_page(request, index_page)

    except ObjectDoesNotExist:
        # Default to simple home page
        context = { 'panels': [ home_panels ] }
        return core.render(request, 'common/docpage.html', **context)
