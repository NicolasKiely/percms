from common import dashboard as dbd
from . import models
from . import views

# App dashboard
App_Dashboard = dbd.App_Dashboard()
App_Dashboard.name = 'Ecommerce'
App_Dashboard.namespace = 'ecom'


# Supplier dashboard
Supplier_Dashboard = dbd.Model_Dashboard(App_Dashboard, models.Supplier)
Supplier_Dashboard.name = 'Supplier'
Supplier_Dashboard.namespace = 'supplier'
Supplier_Dashboard.listing_headers = ['Name']
Supplier_Dashboard.get_listing_record = \
    lambda x: (x.name, )

Supplier_Dashboard.post_edit = dbd.dashboard_view_closure(
    Supplier_Dashboard, views.edit_supplier
)


# Product dashboard
Product_Dashboard = dbd.Model_Dashboard(App_Dashboard, models.Product)
Product_Dashboard.child_of(Supplier_Dashboard, 'supplier')
Product_Dashboard.name = 'Product'
Product_Dashboard.namespace = 'product'
Product_Dashboard.show_on_app_dashboard = False
Product_Dashboard.listing_headers = ['Name']
Product_Dashboard.get_listing_record = \
    lambda x: (x.name, )

Product_Dashboard.post_add = dbd.dashboard_view_closure(
    Product_Dashboard, views.add_product
)
