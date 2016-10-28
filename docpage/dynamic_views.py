''' Handle dynamic component content for docpages '''
from .models import DocPage
from .component_utils import preprocess_text
from proj.models import Proj


def latest_projects(component, args):
    ''' Returns table of latest projects '''
    projects = Proj.objects.order_by('-dt_published')[:5]
    component['table'] = {
        'rows': [[p.get_view_link(), p.dt_published.date()] for p in projects]
    }


def latest_posts(component, args):
    ''' Returns table of latest posts '''
    if len(args) > 0:
        page_objects = DocPage.objects.filter(category=args[0])
    else:
        page_objects = DocPage.objects

    pages = page_objects.order_by('-dt_published')[:5]
    component['table'] = {
        'rows': [[p.get_view_link(), p.dt_published.date()] for p in pages]
    }


def all_posts(component, args):
    ''' Returns table of all posts '''
    if len(args) > 0:
        page_objects = DocPage.objects.filter(category=args[0])
    else:
        page_objects = DocPage.objects

    pages = page_objects.order_by('-dt_published')
    component['table'] = {
        'rows': [[p.get_view_link(), p.dt_published.date()] for p in pages]
    }


def last_post(component, args):
    ''' Returns first component of last post '''
    # Get recent page and component
    try:
        if len(args) > 0:
            page_objects = DocPage.objects.filter(category=args[0])
        else:
            page_objects = DocPage.objects
        page = page_objects.order_by('-dt_published')[0]
        panel = page.panel_set.first()
        other = panel.component_set.first()
    except AttributeError:
        component['src'] = ''
        return

    component['model'] = 'html'
    if other.view == 'text':
        # Text field
        if other.model == 'html':
            component['src'] = other.src

        elif other.model == 'raw':
            component['src'] = '<br />'.join(preprocess_text(other.src))

        else:
            component['src'] = ''
            return
    else:
        component['src'] = ''
        return

    component['src'] = ''.join([
        '<h3>Latest Post: '+ page.title +'</h3>',
        '<small>'+component['src']+'</small><br/>',
        page.get_view_link('View more')
    ])


# Map of dyanmic method names : methods
view_table = {
    'latest_posts': latest_posts,
    'last_post': last_post,
    'latest_projects': latest_projects,
    'all_posts': all_posts
}
