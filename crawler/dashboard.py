from common import dashboard as dbd
from . import models
from . import views


# App dashboard
App_Dashboard = dbd.App_Dashboard()
App_Dashboard.name = 'Crawler'
App_Dashboard.namespace = 'crawler'


# Website dashboard
Website_Dashboard = dbd.Model_Dashboard(App_Dashboard, models.Website)
Website_Dashboard.name = 'Domain'
Website_Dashboard.namespace = 'domain'
Website_Dashboard.listing_headers = ['Domain', 'Module', 'Login Profile']
Website_Dashboard.get_listing_record = \
    lambda x: [x.domain, x.scraper, x.get_profile_name()]


# Crawler dashboard
Crawler_Dashboard = dbd.Model_Dashboard(App_Dashboard, models.Crawler)
Crawler_Dashboard.name = 'Crawler'
Crawler_Dashboard.namespace = 'crawler'
Crawler_Dashboard.listing_headers = ['Domain', 'Status', 'Active State']
Crawler_Dashboard.get_listing_record = \
    lambda x: [x.get_domain(), x.status.title(), x.get_config() +':'+ x.get_state()]

Crawler_Dashboard.post_add = dbd.dashboard_view_closure(
    Crawler_Dashboard, views.add_crawler
)

Crawler_Dashboard.post_edit = dbd.dashboard_view_closure(
    Crawler_Dashboard, views.edit_crawler
)


# Crawler config dashboard
Config_Dashboard = dbd.Model_Dashboard(App_Dashboard, models.Crawler_Config)
Config_Dashboard.name = 'Configuration'
Config_Dashboard.namespace = 'crawler_config'
Config_Dashboard.listing_headers = ['Name']
Config_Dashboard.get_listing_record = \
    lambda x: [x.name]

Config_Dashboard.post_add = dbd.dashboard_view_closure(
    Config_Dashboard, views.add_config
)

Config_Dashboard.post_edit = dbd.dashboard_view_closure(
    Config_Dashboard, views.edit_config
)


# Crawler state
State_Dashboard = dbd.Model_Dashboard(App_Dashboard, models.Crawler_State)
State_Dashboard.child_of(Config_Dashboard, 'config')
State_Dashboard.name = 'Crawler State'
State_Dashboard.namespace = 'crawler_state'
State_Dashboard.listing_headers = ['Name']
State_Dashboard.show_on_app_dashboard = False

State_Dashboard.post_add = dbd.dashboard_view_closure(
    State_Dashboard, views.add_state
)

State_Dashboard.post_edit = dbd.dashboard_view_closure(
    State_Dashboard, views.edit_state
)
