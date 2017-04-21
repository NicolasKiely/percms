from django.conf.urls import url
from . import views, script_views
from .dashboard import Script_Dashboard

urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),

    # Script pages
    Script_Dashboard.url_view_dashboard(r'script/dashboard/$'),
    Script_Dashboard.url_view_editor(r'script/editor/(?P<pk>\d+)/\w*$'),
    Script_Dashboard.url_view_public(r'script/view/(?P<pk>\d+)/\w*$'),
    Script_Dashboard.url_post_add(r'^script/add/$'),
    Script_Dashboard.url_post_edit(r'script/edit/$'),
    Script_Dashboard.url_post_delete(r'^script/delete/$'),

    # Source pages
    url(r'^script/source/commit/$', script_views.commit, name='commit')
]
