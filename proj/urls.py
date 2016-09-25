from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'editor/$', views.editor_list, name='editor_list'),
    url(r'editor/(?P<pk>\d+)/\w*$', views.editor_proj, name='editor'),
    url(r'edit/proj/$', views.edit_proj, name='edit'),
    url(r'add/$', views.add_proj, name='add'),
    url(r'view/(?P<pk>\d+)/\w*$', views.view, name='view')
]
