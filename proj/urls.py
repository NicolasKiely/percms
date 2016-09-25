from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'editor/$', views.editor_list, name='editor_list'),
    url(r'editor/(?P<pk>\d+)/\w*$', views.editor, name='editor'),
    url(r'edit/proj/$', views.edit, name='edit'),
    url(r'add/$', views.add, name='add'),
    url(r'view/(?P<pk>\d+)/\w*$', views.view, name='view')
]
