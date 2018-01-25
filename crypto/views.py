from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
import datetime as dtt

from . import models
from . import utils
import batch_interface
from scripting.utils import get_script_by_name


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


@login_required
def add_portfolio(request, dashboard):
    p = request.POST
    script, source = get_script_by_name(p['script'])
    exchange_name = p['exchange']
    base = models.Currency.objects.get(symbol=p['base'])
    portfolio = models.Portfolio(
        script = source,
        exc = models.Exchange.objects.get(name=exchange_name),
        key = models.API_Key.objects.get(name=p['key']),
        base_currency = base,
        active = ('active' in p and p['active'])
    )
    portfolio.save()

    # Get trade pairs
    for trade_currency in p['trade'].split(' '):
        trade_name = trade_currency.strip(',')
        try:
            pair = utils.get_currency_pair(exchange_name, base.symbol, trade_name)
        except models.Pair.DoesNotExist:
            raise Backtest_Exception(
                'Currency pair %s_%s not found' % (base.symbol, trade_name)
            )
        portfolio.pairs.add(pair)
    return HttpResponseRedirect(dashboard.reverse_dashboard())


@login_required
def edit_portfolio(request, dashboard):
    p = request.POST
    portfolio = get_object_or_404(models.Portfolio, pk=p['pk'])
    exchange_name = p['exchange']
    base = models.Currency.objects.get(symbol=p['base'])
    script, source = get_script_by_name(p['script'])
    
    portfolio.script = source
    portfolio.exc = models.Exchange.objects.get(name=exchange_name)
    portfolio.key = models.API_Key.objects.get(name=p['key'])
    portfolio.base_currency = base
    portfolio.active = 'active' in p
    
    # Get trade pairs
    portfolio.pairs.clear()
    for trade_currency in p['trade'].split(' '):
        trade_name = trade_currency.strip(',')
        try:
            pair = utils.get_currency_pair(exchange_name, base.symbol, trade_name)
        except models.Pair.DoesNotExist:
            raise Backtest_Exception(
                'Currency pair %s_%s not found' % (base.symbol, trade_name)
            )
        portfolio.pairs.add(pair)

    portfolio.save()
    return HttpResponseRedirect(dashboard.reverse_dashboard())


@login_required
def add_exchange(request, dashboard):
    p = request.POST
    exc = models.Exchange(name=p['name'])
    exc.save()
    return HttpResponseRedirect(dashboard.reverse_dashboard())

@login_required
def edit_exchange(request, dashboard):
    p = request.POST
    exc = get_object_or_404(models.Exchange, pk=p['pk'])
    exc.name = p['name']
    exc.save()
    return HttpResponseRedirect(dashboard.reverse_dashboard())
