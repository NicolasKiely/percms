from django.conf.urls import include, url

import docpage.views as docpage_views
import filemanager.views as file_views

docpage_url = r'^(?P<category>\w+)/(?P<title>[\w-]+)(.html)?'
file_url = r'^(?P<resource>[\w\.]+)$'

urlpatterns = [
    url(docpage_url, docpage_views.view_by_name, name='docpage'),
    url(file_url, file_views.view_by_name, name='static')
]
