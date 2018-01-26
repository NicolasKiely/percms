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

    # Parse list of pairs
    marker_map = {} # Mapping of currency tuple to list of periods
    tracking_pairs = p['pairs'].split('\n')
    for tracker in tracking_pairs:
        pair_name, periods = [s.strip() for s in tracker.split(':')]
        pair_tuple = tuple(pair_name.split('_'))
        marker_map[pair_tuple] = [int(p.strip()) for p in periods.split(',')]
        

    # Get old trading pairs
    pairs = exc.pair_set.all()
    for pair in pairs:
        # Get monitoring markers
        for marker in pair.candle_marker_set.all():
            marker.active = False
            marker.save()
    
    # Update trading pairs
    for pair_name, periods in marker_map.iteritems():
        # Get currency pair
        c1, c2 = pair_name
        pair, created = models.Pair.objects.get_or_create(
            exc=exc, c1=c1, c2=c2
        )
        if not created:
            pair.save()

        # Get markers
        for period in periods:
            marker, created = models.Candle_Marker.objects.get_or_create(
                pair=pair, period=period
            )
            marker.active = True
            marker.save()


    exc.save()
    return HttpResponseRedirect(dashboard.reverse_dashboard())
