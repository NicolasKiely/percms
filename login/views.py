from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from common import core
from . import forms


def user_account(request):
    ''' User account page, or login page '''
    # Login page
    context = {
        'form': forms.login,
        'formid': 'login-form',
        'logid': 'login-log',
        'action': '/percms/account/login',
        'validators': ['login/login_validator.js'],
        'title': 'Editor Log In'
    }
    return core.renderform(request, context)


def user_login(request):
    ''' Logs user in '''
    uname = request.POST['login-email']
    upass = request.POST['login-passwd']
    user = authenticate(username=uname, password=upass)
    if user:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect('/percms/account/login-success')
        else:
            return HttpResponseRedirect('/percms/account/login-inactive')
    else:
        context = {
            'form'  : forms.login,
            'formid': 'login-form',
            'logid' : 'login-log',
            'action': '/percms/account/login',
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
