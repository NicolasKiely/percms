from django.conf.urls import url
from . import views
from .dashboard import App_Dashboard, Supplier_Dashboard, Product_Dashboard


urlpatterns = [
    App_Dashboard.url_view_dashboard(r'^dashboard/$'),

    # Supplier pages
    Supplier_Dashboard.url_view_dashboard(r'^supplier/dashboard/$'),
    Supplier_Dashboard.url_view_editor(r'^supplier/editor/(?P<pk>\d)/w*$'),
    Supplier_Dashboard.url_view_public(r'^supplier/view/(?P<pk>\d)/w*$'),
    Supplier_Dashboard.url_post_add(r'^supplier/add/$'),
    Supplier_Dashboard.url_post_edit(r'^supplier/edit/$'),
    Supplier_Dashboard.url_post_delete(r'^supplier/delete/$'),

    # Product pages
    Product_Dashboard.url_view_dashboard(r'^product/dashboard/$'),
    Product_Dashboard.url_view_editor(r'^product/editor/(?P<pk>\d)/w*$'),
    Product_Dashboard.url_view_public(r'^product/view/(?P<pk>\d)/w*$'),
    Product_Dashboard.url_post_add(r'^product/add/$'),
    Product_Dashboard.url_post_edit(r'^product/edit/$'),
    Product_Dashboard.url_post_delete(r'^product/delete/$')
]
