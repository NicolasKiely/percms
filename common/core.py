import django.shortcuts
import percms.settings
from django.http import HttpResponse

__GOOGLE_API = 'https://ajax.googleapis.com/ajax'
__BOOTSTRAP =  'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5'

# Resolve local vs cdn assets
if percms.settings.USE_LOCAL_ASSETS:
    __jquery_js = '/static/common/jquery-1.11.3.min.js'
    __bootst_js = '/static/common/bootstrap.min.js'
    __bootst_css = '/static/common/bootstrap.min.css'
else:
    __jquery_js = __GOOGLE_API + '/libs/jquery/1.11.3/jquery.min.js'
    __bootst_js = __BOOTSTRAP + '/js/bootstrap.min.js'
    __bootst_css = __BOOTSTRAP + '/css/bootstrap.min.css'


__CORE_PAGE_CONFIG = {
    'page': {
        'site': 'PerCMS Portfolio',
        'title': '',
        'js': {
            'jquery': __jquery_js,
            'bootstrap': __bootst_js
        },
        'css': {
            'bootstrap': __bootst_css
        },
        # Drop-down menu for logged in users
        'user_menu': [
            ('login:account', 'My Dashboard'),
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
