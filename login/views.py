from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from common import core
from . import forms
from docpage.models import DocPage
from filemanager.models import Meta_File


def user_account(request):
    ''' User account page, or login page '''
    if request.user.is_authenticated():
        # Account dashboard
        image_objs = Meta_File.objects.filter(is_img=True).order_by('-dt_uploaded')[:6]
        image_ids = [str(image.id) for image in image_objs]
        context = {
            'docpages': DocPage.objects.order_by('-dt_editted')[:5],
            'images': [{'id':i, 'url':'images/'+i} for i in image_ids]
        }
        return core.render(request, 'login/dashboard.html', **context)

    else:
        # Login page
        context = {
            'form': forms.login,
            'formid': 'login-form',
            'logid': 'login-log',
            'action': reverse('login:login'),
            'validators': ['login/login_validator.js'],
            'title': 'Editor Log In'
        }
        return core.renderform(request, context)


def user_login(request):
    ''' Logs user in '''
    uname = request.POST['login-name']
    upass = request.POST['login-passwd']
    user = authenticate(username=uname, password=upass)
    if user:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse('login:account'))
        else:
            return HttpResponseRedirect(reverse('login:login-inactive'))
    else:
        context = {
            'form'  : forms.login,
            'formid': 'login-form',
            'logid' : 'login-log',
            'action': reverse('login:login'),
            'validators': ['login/login_validator.js'],
            'title' : 'Log In',
            'error' : 'Error in authenticating account'+ uname
        }
        return core.renderform(request, context)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def user_login_success(request):
    ''' Success login page '''
    return core.render(request, 'login/login-conf.html')


def user_login_inactive(request):
    ''' Inactive login page '''
    return core.render(request, 'login/login-inactive.html')
