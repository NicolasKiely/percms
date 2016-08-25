from django.shortcuts import render
from common import core
from login import forms

# Index page form fields
index_forms = {
    'signup_form': forms.signup,
    'login_form': forms.login
}

def index(request):
    return core.render(request, 'home/index.html', **index_forms)
