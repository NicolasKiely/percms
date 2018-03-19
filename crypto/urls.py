from django.conf.urls import url
from . import dashboard
from . import views


urlpatterns = [
    dashboard.App_Dashboard.url_view_dashboard(r'^dashboard/$'),
    dashboard.App_Dashboard.custom_url(
        r'weekly_csv/(?P<pk>\d+)/', views.view_weekly_csv, 'weekly_csv'
    )
] \
    + dashboard.Key_Dashboard.create_standard_urls() \
    + dashboard.BT_Dashboard.create_standard_urls() \
    + dashboard.Port_Dashboard.create_standard_urls() \
    + dashboard.Exc_Dashboard.create_standard_urls()
