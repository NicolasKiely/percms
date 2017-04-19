from common.dashboard import App_Dashboard, Model_Dashboard
from .models import Website


# App dashboard
Dashboard = App_Dashboard()
Dashboard.name = 'Crawler'
Dashboard.namespace = 'crawler'


# Website dashboard
Website_Dashboard = Model_Dashboard(Dashboard, Website)
Website_Dashboard.name = 'Domain'
Website_Dashboard.namespace = 'domain'
Website_Dashboard.listing_headers = ['Domain', 'Module', 'Login Profile', 'URL']
Website_Dashboard.get_listing_record = \
    lambda x: (x.domain, x.scraper, x.profile.name)
