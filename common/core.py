import django.shortcuts
from django.http import HttpResponse

__GOOGLE_API = 'https://ajax.googleapis.com/ajax'
__BOOTSTRAP =  'http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5'

__CORE_PAGE_CONFIG = {
    'page': {
        'site': 'PerCMS Portfolio',
        'title': '',
        'js': {
            'jquery': __GOOGLE_API + '/libs/jquery/1.11.3/jquery.min.js',
            'bootstrap': __BOOTSTRAP + '/js/bootstrap.min.js'
        },
        'css': {
            'bootstrap': __BOOTSTRAP + '/css/bootstrap.min.css'
        },
        # Drop-down menu for logged in users
        'user_menu': [
            #('user:dashboard', 'My Dashboard'),
            #('user:settings', 'My Settings'),
            ('index', 'Site Home'),
            ('login:logout', 'Logout')
        ],
        # Alternative menu for non-logged in users
        'anon_menu': []
    },

    'user': None
}


def render(request, template_path, **kwargs):
    ''' Wrapper for django render function '''
    context = __CORE_PAGE_CONFIG.copy()
    for key, value in kwargs.iteritems():
        context[key] = value

    if request.user.is_authenticated():
        context['user'] = request.user
    return django.shortcuts.render(request, template_path, context) 


def renderform(request, formcontext):
    ''' Renders generic form '''
    return render(request, 'common/singleform.html', **formcontext)
