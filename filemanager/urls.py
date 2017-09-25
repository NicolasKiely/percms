from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^download/(?P<pk>\d+)$', views.download, name='download'),
    url(r'^describe/(?P<pk>\d+)$', views.describe, name='describe')
]
