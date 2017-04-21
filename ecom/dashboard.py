from common import dashboard as dbd
from . import models

# App dashboard
App_Dashboard = dbd.App_Dashboard()
App_Dashboard.name = 'Ecommerce'
App_Dashboard.namespace = 'ecom'


# Supplier dashboard
Supplier_Dashboard = dbd.Model_Dashboard(App_Dashboard, models.Supplier)
Supplier_Dashboard.name = 'Supplier'
Supplier_Dashboard.namespace = 'supplier'
Supplier_Dashboard.listing_headers = ['Name', 'URL']
Supplier_Dashboard.get_listing_record = \
    lambda x: (x.name, )
