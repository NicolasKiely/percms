from django.conf.urls import url
from . import dashboard
from . import views


urlpatterns = [
    dashboard.App_Dashboard.url_view_dashboard(r'^dashboard/$')
]
