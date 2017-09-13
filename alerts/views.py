from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils import timezone

from . import models

@login_required
def add_alert(request, dashboard):
    p = request.POST
    alert = models.Alert(
        message=p['message'],
        name=p['name'],
        stamp=timezone.now()
    )
    alert.save()
    return HttpResponseRedirect(dashboard.reverse_dashboard())


@login_required
def edit_alert(request, dashboard):
    p = request.POST
    alert = get_object_or_404(models.Alert, pk=p['pk'])
    alert.name = p['name']
    alert.message = p['message']
    alert.save()
    return HttpResponseRedirect(dashboard.reverse_dashboard())
