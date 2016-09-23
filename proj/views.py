from django.shortcuts import render


def editor_list(request):
    ''' Top-levbel editor page for projects '''
    context = {
    }
    return core.render(request, '
