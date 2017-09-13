from common import dashboard as dbd
from . import models
from . import views

# App dashboard
App_Dashboard = dbd.App_Dashboard()
App_Dashboard.name = 'Alerts'
App_Dashboard.namespace = 'alerts'

# Alerts dashboard
Alert_Dashboard = dbd.Model_Dashboard(App_Dashboard, models.Alert)
Alert_Dashboard.name = 'Messages'
Alert_Dashboard.namespace = 'message'
Alert_Dashboard.listing_headers = ['Name']
Alert_Dashboard.get_listing_record = \
    lambda x: [x.name]

Alert_Dashboard.post_add = dbd.dashboard_view_closure(
    Alert_Dashboard, views.add_alert
)

Alert_Dashboard.post_edit = dbd.dashboard_view_closure(
    Alert_Dashboard, views.edit_alert
)
