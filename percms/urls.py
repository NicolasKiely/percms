"""percms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^percms/account/', include('login.urls', namespace='login')),
    url(r'^percms/docpage/', include('docpage.urls', namespace='docpage')),
    url(r'^percms/files/', include('filemanager.urls', namespace='file')),
    url(r'^percms/project/', include('proj.urls', namespace='project')),
    url(r'^percms/app/gametracker/', include('gametracker.urls', namespace='gametracker')),
    url(r'^percms/app/crawler/', include('crawler.urls', namespace='crawler')),
    url(r'^$', include('home.urls')),
    url(r'^percms/admin/', include(admin.site.urls)),
    url(r'', include('percms.fallback_urls', namespace='fallback'))
]
