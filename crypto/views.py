import csv
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
import datetime as dtt
from django.utils import timezone

from . import models
from . import utils
from . import poloniex_api
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
        'dt_stop': p['dt_stop'],
        'period': p['period']
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
    portfolio.period = int(p['period'])
    portfolio.position_limit = float(p['pos_limit'])
    portfolio.buy_limit = float(p['buy_limit'])
    
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
def view_portfolio(request, dashboard, pk):
    obj = get_object_or_404(dashboard.model, pk=pk)
    pairs = [p for p in obj.pairs.all()]
    balances = {p.name(): 0.0 for p in pairs}
    position_list = models.Portfolio_Position.objects.filter(portfolio=obj).all()
    positions = {p.pair.name(): p.position for p in position_list}
    stop_str = lambda p: str(p.stoploss) if p.stoploss else ''
    stoplosses = {p.pair.name(): stop_str(p) for p in position_list}
    base_name = obj.base_currency.symbol
    base_amt = 0.0

    if obj.exc.name == 'Poloniex':
        # Read poloniex balance
        polo = poloniex_api.poloniex(str(obj.key.key), str(obj.key.secret))
        balance_vals = polo.returnBalances()
        for c, v in balance_vals.iteritems():
            fv = float(v)
            if fv > 0:
                if base_name == c:
                    base_amt = fv
                else:
                    balances[base_name+'_'+c] = fv

    for pair in pairs:
        if not(pair.name() in positions):
            positions[pair.name()] = ''

    context = {
        'pairs': [
            {
                'name': p.c2, 'balance': balances[p.name()],
                'position': positions[p.name()],
                'stoploss': stoplosses[p.name()]
            }
            for p in pairs
        ],
        'base': {
            'name': base_name,
            'balance': base_amt
        },
        'limit': {
            'position': obj.position_limit,
            'buy': obj.buy_limit
        },
        'portfolio_id': pk
    }
    return dashboard.view_model(request, obj, context)


@login_required
def view_exchange(request, dashboard, pk):
    obj = get_object_or_404(dashboard.model, pk=pk)
    markers = []
    pairs = obj.pair_set.all()
    for pair in pairs:
        pair_str = pair.c1 +'_'+ pair.c2

        # Get monitoring markers
        for marker in pair.candle_marker_set.filter(active=True).all():
            markers.append({
                'pair': pair_str, 'period': str(marker.period),
                'start': str(marker.data_start), 'end': str(marker.data_stop)
            })

    context = { 'markers': markers }
    return dashboard.view_model(request, obj, context)
    

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


def view_weekly_csv(request, pk):
    portfolio = get_object_or_404(models.Portfolio, pk=pk)

    # Get records
    dt_start = timezone.now() - dtt.timedelta(days=7)
    records = models.Portfolio_History.objects.filter(
        stamp__gte=dt_start
    ).order_by('stamp').all()

    # Compile positions
    position_records = []
    pair_names = set()
    for record in records:
        positions = record.portfolio_position_history_set.all()
        position_map = {p.pair.name(): p for p in positions}
        position_records.append(position_map)

        for pair_name in position_map.keys():
            pair_names.add(pair_name)

    # Create response
    response = HttpResponse(content_type='text/csv')
    file_name = 'weekly_portfolio_'+portfolio.key.name+'.csv'
    response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
    writer = csv.writer(response)

    # Write header
    pair_list = list(pair_names)
    header = ['Time', 'Base Holding', 'Total Value']
    for pair_name in pair_list:
        # For each pair: Amount, Value
        header.append(pair_name+' Amount')
        header.append(pair_name+' Value')
    writer.writerow(header)

    # Write body
    for record, position in zip(records, position_records):
        row = [record.stamp, record.base_holding, record.total_holding]
        for pair_name in pair_list:
            # For each pair: Amount, Value
            if pair_name in position:
                row.append(position[pair_name].amount_held)
                row.append(position[pair_name].value_held)
            else:
                row.append(0.0)
                row.append(0.0)
        writer.writerow(row)
    return response
