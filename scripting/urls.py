from django.conf.urls import url
from . import views, script_views
from .dashboard import Script_Dashboard

urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),

    # Script pages
    Script_Dashboard.url_view_dashboard(r'script/dashboard/$'),
    Script_Dashboard.url_view_editor(r'script/editor/(?P<pk>\d+)/\w*$'),

    url(r'^script/view/(?P<pk>\d+)/\w*$', script_views.view, name='script_view'),
    url(r'^script/add/$', script_views.add, name='add_script'),
    url(r'^script/edit/$', script_views.edit, name='edit_script'),
    url(r'^script/delete/$', script_views.delete, name='delete_script')
]
