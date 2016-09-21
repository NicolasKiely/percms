''' Handle dynamic component content for docpages '''
from .models import DocPage


def latest_posts(component):
    ''' Returns table of latest posts '''
    pages = DocPage.objects.order_by('-dt_editted')[:5]
    component['table'] = {
        'rows': [[p.get_view_link(), p.dt_editted.date()] for p in pages]
    }


# Map of dyanmic method names : methods
view_table = {
    'latest_posts': latest_posts
}
