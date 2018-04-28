""" Celery endpoints for trading methods """
from __future__ import absolute_import, unicode_literals
import time
from celery import group
from django.utils import timezone as tz
from percms.celery import app
from exchange.utils import get_interface_class
import crypto.utils
import crypto.models
import exchange.models


@app.task()
def load_exchange_tickers(exchange_id, portfolio_id, do_sleep=False):
    """ Fetches and saves exchange tickers

    :param exchange_id: ID of exchange to pull data from
    :param portfolio_id: ID used for connection to exchange
    :param do_sleep: If true, applies rate limiting pause
    """
    exc = crypto.models.Exchange.objects.get(pk=exchange_id)
    portfolio = crypto.models.Portfolio.objects.get(pk=portfolio_id)
    interface = get_interface_class(exc.name)(portfolio.key)
    if do_sleep:
        interface.sleep()
    print("Loading ticker prices from exchange %s" % str(exchange))
    tickers = interface.get_ticker()

    now = tz.now()
    for pair, value in tickers.items():
        c_pair = crypto.utils.get_currency_pair(exc, pair[0], pair[1])
        try:
            # Get existing ticker
            t = exchange.models.Ticker.objects.get(pair=c_pair)
        except exchange.models.Ticker.DoesNotExist:
            t = exchange.models.Ticker(pair=c_pair)

        # Update ticker
        t.pair = c_pair
        t.last = value
        t.stamp = now
        t.save()

    # Save to database
    print(tickers)


@app.task()
def load_exchange_balances(exchange_id, portfolio_ids, do_sleep=False):
    """ Fetchs and saves exchange balances from given exchange

    :param exchange_id: ID of exchange to pull data from
    :param portfolio_ids: List of portfolio IDs
    :param do_sleep: If true, applies initial rate limiting pause
    """
    exchange = crypto.models.Exchange.objects.get(pk=exchange_id)
    interface_class = get_interface_class(exchange.name)
    print("Loading balances from exchange %s" % str(exchange))

    first = not do_sleep
    t = 0
    for portfolio_id in portfolio_ids:
        # Fetch connection to exchange for a given account
        portfolio = crypto.models.Portfolio.objects.get(pk=portfolio_id)
        interface = interface_class(portfolio.get_api_key())

        if first:
            first = False
        else:
            interface.sleep(t)
            t = time.time()

        balance = interface.get_balance()
        print(balance)


def evaluate_portfolios(commit=True):
    """ Triggers evaluation of all active portfolios

    :param commit: Whether or not to commit trading signals to exchange
    :return: None
    """
    portfolios = crypto.models.Portfolio.objects.filter(active=True).all()

    # Build {exchange_id: [portfolio_ids, ...]} mapping
    exchange_map = {}
    for portfolio in portfolios:
        if portfolio.exc_id in exchange_map:
            exchange_map[portfolio.exc_id].append(portfolio.id)
        else:
            exchange_map[portfolio.exc_id] = [portfolio.id]

    # Fetch tickers from exchanges
    results = group(
        load_exchange_tickers.s(ex_id, exchange_map[ex_id][0])
        for ex_id in exchange_map.keys()
    )()
    results.get(timeout=30)

    # Synchornously fetch balances from exchanges
    results = group(
        load_exchange_balances.s(ex_id, p_ids, True) for ex_id, p_ids in exchange_map.items()
    )()
    results.get(timeout=30)
