from django.conf.urls import url
from . import views

from . import dashboard


urlpatterns = [
    dashboard.App_Dashboard.url_view_dashboard(r'^dashboard/$'),

] \
    + dashboard.Alert_Dashboard.create_standard_urls()
