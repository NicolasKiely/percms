from common.dashboard import App_Dashboard, Model_Dashboard
from .models import Script, Source


# App dashboard
Dashboard = App_Dashboard()
Dashboard.name = 'Scripting'
Dashboard.namespace = 'script'


# Script dashboard
Script_Dashboard = Model_Dashboard(Dashboard, Script)
Script_Dashboard.name = 'Script'
Script_Dashboard.namespace = 'script'
Script_Dashboard.listing_headers = ['Category', 'Name']
Script_Dashboard.get_listing_record = \
    lambda x: (x.category, x.name)
