from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'^editor/', views.editor, name='editor'),
    url(r'^add-page/', views.add_page, name='add_page')
]
