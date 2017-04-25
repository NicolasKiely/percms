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
    lambda x: (x.domain, x.scraper, x.get_profile_name())


# Crawler dashboard
Crawler_Dashboard = dbd.Model_Dashboard(App_Dashboard, models.Crawler)
Crawler_Dashboard.name = 'Crawler'
Crawler_Dashboard.namespace = 'crawler'
Crawler_Dashboard.listing_headers = ['Domain', 'Status', 'Active State']
Crawler_Dashboard.get_listing_record = \
    lambda x: (x.get_domain(), x.status, x.get_config() +':'+ x.get_state())

Crawler_Dashboard.post_add = dbd.dashboard_view_closure(
    Crawler_Dashboard, views.add_crawler
)


# Crawler config dashboard
Config_Dashboard = dbd.Model_Dashboard(App_Dashboard, models.Crawler_Config)
Config_Dashboard.name = 'Configuration'
Config_Dashboard.namespace = 'crawler_config'
Config_Dashboard.listing_headers = ['Name']
Config_Dashboard.get_listing_record = \
    lambda x: [x.name]
