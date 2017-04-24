from common import dashboard as dbd
from . import models


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
Crawler_Dashboard.listing_headers = ['Domain', 'Status']
Crawler_Dashboard.get_listing_record = \
    lambda x: (x.get_domain(), x.status, x.get_config(), x.get_state())
