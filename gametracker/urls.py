from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^league/editor/$', views.editor_league_list, name='editor_list')
]
