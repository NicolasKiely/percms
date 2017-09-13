from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from . import models

@login_required
def add_alert(request, dashboard):
    return HttpResponseRedirect(dashboard.reverse_dashboard())


@login_required
def edit_alert(request, dashboard):
    return HttpResponseRedirect(dashboard.reverse_dashboard())
