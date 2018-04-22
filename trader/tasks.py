""" Celery endpoints for trading methods """
from __future__ import absolute_import, unicode_literals
from celery import Celery
from percms.celery import app
import crypto.models


@app.task(bind=True)
def evaluate_portfolios(self, commit=True):
    """ Primary trigger for evaluating all portfolios

    Workflow subtasks:
        - Fetch balances for all portfolios
        - Branch off and compute trading positions for all accounts
        - Execute trades of all portfolios
    """
    print("Evaluating portfolios!")
    portfolios = crypto.models.Portfolio.objects.filter(active=True).all()

    # Fetch balances from exchanges
    exchange_id_set = set([p.exc_id for p in portfolios])
    for exchange_id in exchange_id_set:
        print("Loading balances from exchange #%s" % exchange_id)

    for portfolio in portfolios:
        # Fetch account balances
        print("Evaluating %s" % portfolio)