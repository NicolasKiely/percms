from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
import datetime as dtt

from . import models
from . import utils
import batch_interface


@login_required
def add_key(request, dashboard):
    p = request.POST
    apikey = models.API_Key(
        name=p['name'],
        key=p['key'],
        secret=p['secret']
    )
    apikey.save()
    return HttpResponseRedirect(dashboard.reverse_dashboard())


@login_required
def edit_key(request, dashboard):
    p = request.POST
    apikey = get_object_or_404(models.API_Key, pk=p['pk'])
    apikey.name = p['name']
    apikey.key = p['key']
    apikey.secret = p['secret']
    apikey.save()
    return HttpResponseRedirect(dashboard.reverse_dashboard())



@login_required
def add_backtest(request, dashboard):
    p = request.POST
    batch_interface.request('crypto', 'backtest', {
        'exchange_name': p['exchange'],
        'base_currency': p['base'],
        'trade_currencies': p['trade'],
        'script_name': p['script'],
        'dt_start': p['dt_start'],
        'dt_stop': p['dt_stop']
    })

    return HttpResponseRedirect(dashboard.reverse_dashboard())
