''' Url patterns '''
from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'^$', views.user_account, name='account'),
    url(r'^login$', views.user_login, name='login'),
    url(r'^login-success$', views.user_login_success),
    url(r'^login-inactive$', views.user_login_inactive),
    url(r'^logout$', views.user_logout, name='logout')
]
