from django.conf.urls import url
from . import views
from .dashboard import Supplier_Dashboard


urlpatterns = [
    url(r'^dashboard/$', views.view_dashboard, name='dashboard'),

    # Supplier pages
    Supplier_Dashboard.url_view_dashboard(r'^supplier/dashboard/$'),
    Supplier_Dashboard.url_view_editor(r'^supplier/editor/(?P<pk>\d)/w*$'),
    Supplier_Dashboard.url_view_public(r'^supplier/view/(?P<pk>\d)/w*$'),
    Supplier_Dashboard.url_post_add(r'^supplier/add/$'),
    Supplier_Dashboard.url_post_edit(r'^supplier/edit/$'),
    Supplier_Dashboard.url_post_delete(r'^supplier/delete/$')
]
