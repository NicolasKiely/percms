from django.conf.urls import include, url
from . import views

editor_list_pat = '^editor/'
editor_page_pat = editor_list_pat + '(?P<pk>\d+)/\w*'

urlpatterns = [
    url(editor_list_pat +'$', views.editor_list, name='editor_list'),
    url(editor_page_pat +'$', views.editor_page, name='editor_page'),
    url(r'^add-page/$', views.add_page, name='add_page')
]
