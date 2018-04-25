""" Celery endpoints for trading methods """
from __future__ import absolute_import, unicode_literals
import time
from celery import group
from percms.celery import app
from exchange.utils import get_interface_class
import crypto.models


@app.task(bind=True)
def load_exchange_balances(self, exchange_id, portfolio_ids):
    """ Fetchs and saves exchange balances from given exchange

    :param self: Task instance
    :param exchange_id: ID of exchange to pull data from
    :param portfolio_ids: List of portfolio IDs
    :return: None
    """
    exchange = crypto.models.Exchange.objects.get(pk=exchange_id)
    interface_class = get_interface_class(exchange.name)
    print("Loading balances from exchange %s" % str(exchange))

    first = True
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

    # Fetch balances from exchanges
    results = group(
        load_exchange_balances.s(ex_id, p_ids) for ex_id, p_ids in exchange_map.items()
    )()
    results.get(timeout=30)
