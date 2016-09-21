''' Handle dynamic component content for docpages '''
from .models import DocPage
from .component_utils import preprocess_text


def latest_posts(component):
    ''' Returns table of latest posts '''
    pages = DocPage.objects.order_by('-dt_published')[:5]
    component['table'] = {
        'rows': [[p.get_view_link(), p.dt_editted.date()] for p in pages]
    }


def last_post(component):
    ''' Returns first component of last post '''
    # Get recent page and component
    try:
        page = DocPage.objects.order_by('-dt_published')[0]
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
    'last_post': last_post
}
