from django.core.urlresolvers import reverse
import django.shortcuts
import percms.settings
import percms.safesettings
from django.http import HttpResponse

__GOOGLE_API = 'https://ajax.googleapis.com/ajax'
__BOOTSTRAP =  'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5'

# Resolve local vs cdn assets
if percms.safesettings.USE_LOCAL_ASSETS:
    __jquery_js = '/static/common/jquery-1.11.3.min.js'
    __bootst_js = '/static/common/bootstrap.min.js'
    __bootst_css = '/static/common/bootstrap.min.css'
else:
    __jquery_js = __GOOGLE_API + '/libs/jquery/1.11.3/jquery.min.js'
    __bootst_js = __BOOTSTRAP + '/js/bootstrap.min.js'
    __bootst_css = __BOOTSTRAP + '/css/bootstrap.min.css'


def get_core_config():
    ''' Returns copy of core page config '''
    return {
        'page': {
            'site': percms.safesettings.SITE_TITLE,
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
                (reverse('login:account'), 'My Dashboard'),
                (reverse('file:upload'), 'Upload Files'),
                (reverse('index'), 'Site Home'),
                (reverse('admin:index'), 'Site Admin'),
                (reverse('login:logout'), 'Logout')
            ],
            # Alternative menu for non-logged in users
            'anon_menu': [
                (reverse('index'), 'Site Home'),
                (reverse('fallback_docpage:view', args=('site', 'about-site')), 'About This Site'),
                (reverse('fallback_docpage:view', args=('site', 'about-me')), 'About Me'),
                (reverse('login:account'), 'Login')
            ]
        },

        'user': None
    }


def render(request, template_path, **kwargs):
    ''' Wrapper for django render function '''
    context = get_core_config()
    for key, value in kwargs.iteritems():
        context[key] = value

    if request.user.is_authenticated():
        context['user'] = request.user
    return django.shortcuts.render(request, template_path, context) 


def renderform(request, formcontext):
    ''' Renders generic form '''
    return render(request, 'common/singleform.html', **formcontext)
