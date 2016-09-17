from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^(?P<category>\w+)/(?P<title>\w+)(.html)?', views.view_by_name)
]
