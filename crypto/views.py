from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
import datetime as dtt

from . import models
from . import utils
from scripting.utils import get_script_by_name
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
    #script, source = get_script_by_name(p['script'])
    #c1, c2 = p['pair'].split('_')
    #pair = utils.get_currency_pair(p['exchange'], c1, c2)
    #backtest = models.Back_Test(
    #    status = models.BACK_TEST_READY,
    #    script = source,
    #    pair = pair,
    #    dt_start = dtt.datetime.strptime(p['dt_start'], '%Y-%m-%d'),
    #    dt_stop = dtt.datetime.strptime(p['dt_stop'], '%Y-%m-%d')
    #)
    #backtest.save()
    args = {}
    batch_interface.request('crypto', 'backtest', args)

    return HttpResponseRedirect(dashboard.reverse_dashboard())
