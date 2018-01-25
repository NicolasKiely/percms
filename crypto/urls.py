from django.conf.urls import url
from . import dashboard
from . import views


urlpatterns = [
    dashboard.App_Dashboard.url_view_dashboard(r'^dashboard/$')
] \
    + dashboard.Key_Dashboard.create_standard_urls() \
    + dashboard.BT_Dashboard.create_standard_urls() \
    + dashboard.Port_Dashboard.create_standard_urls() \
    + dashboard.Exc_Dashboard.create_standard_urls()
