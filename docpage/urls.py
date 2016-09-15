from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'^editor/$', views.editor_list, name='editor_list'),
    url(r'^editor/(?P<pk>\d+)/\w*$', views.editor_page, name='editor_page'),
    url(r'^edit/docpage/$', views.edit_page, name='edit_page'),
    url(r'^add-page/$', views.add_page, name='add_page'),
    url(r'^view/(?P<pk>\d+)/\w*$', views.view_page, name='view_page')
]
