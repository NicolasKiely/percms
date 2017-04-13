from django.conf.urls import url
from . import views

urlpatterns = [
    # Crawler manager portal
    url(r'^dashboard/$', views.dashboard, name='dashboard'),

    # Crawler view portal
    url(r'^view/$', views.public_view, name='view')
]
