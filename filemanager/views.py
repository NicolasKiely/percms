from django.shortcuts import render
from common import core


def upload(request):
    ''' Upload file page '''
    return core.render(request, 'filemanager/upload.html', **{})
