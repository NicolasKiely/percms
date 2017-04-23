from django.conf.urls import url
from . import views
from . import domain_views
from .dashboard import App_Dashboard, Website_Dashboard


urlpatterns = [
    # Crawler manager and view portals
    App_Dashboard.url_view_dashboard(r'^dashboard/$'),
    url(r'^view/$', views.public_view, name='view'),

    # Crawler pages

    # Domain management pages
    url(r'^domain/dashboard/$', domain_views.dashboard, name='domain_dashboard'),
    url(r'^domain/editor/(?P<pk>\d+)/[\w\.]*$', domain_views.editor, name='domain_editor'),
    url(r'^domain/view/(?P<pk>\d+)/[\w\.]*$', domain_views.view, name='domain_view'),
    url(r'^domain/add/$', domain_views.add, name='add_domain'),
    url(r'^domain/edit/$', domain_views.edit, name='edit_domain'),
    url(r'^domain/delete/$', domain_views.delete, name='delete_domain')
]
