from common import dashboard as dbd
from .models import Website


# App dashboard
App_Dashboard = dbd.App_Dashboard()
App_Dashboard.name = 'Crawler'
App_Dashboard.namespace = 'crawler'


# Website dashboard
Website_Dashboard = dbd.Model_Dashboard(App_Dashboard, Website)
Website_Dashboard.name = 'Domain'
Website_Dashboard.namespace = 'domain'
Website_Dashboard.listing_headers = ['Domain', 'Module', 'Login Profile']
Website_Dashboard.get_listing_record = \
    lambda x: (x.domain, x.scraper, x.get_profile_name())
