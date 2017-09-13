from django.conf.urls import url
from . import views

from .dashboard import App_Dashboard


urlpatterns = [
    App_Dashboard.url_view_dashboard(r'dashboard/$')
]
