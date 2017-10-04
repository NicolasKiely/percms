from django.conf.urls import url
from . import views, script_views
from . import dashboard

urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),

    # Script pages
    dashboard.Script_Dashboard.url_view_dashboard(r'script/dashboard/$'),
    dashboard.Script_Dashboard.url_view_editor(r'script/editor/(?P<pk>\d+)/\w*$'),
    dashboard.Script_Dashboard.url_view_public(r'script/view/(?P<pk>\d+)/\w*$'),
    dashboard.Script_Dashboard.url_post_add(r'^script/add/$'),
    dashboard.Script_Dashboard.url_post_edit(r'script/edit/$'),
    dashboard.Script_Dashboard.url_post_delete(r'^script/delete/$'),

    # Source pages
    url(r'^script/source/commit/$', script_views.commit, name='commit'),
    dashboard.Source_Dashboard.url_view_editor(r'^source/editor/(?P<pk>\d+)/'),
    dashboard.Source_Dashboard.url_view_public(r'^source/view/(?P<pk>\d+)/'),
    dashboard.Source_Dashboard.url_post_edit(r'^source/edit/$'),
    dashboard.Source_Dashboard.url_post_delete(r'^source/delete/$')
] + \
    dashboard.Log_Dashboard.create_standard_urls()
