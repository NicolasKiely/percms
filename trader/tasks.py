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


    for portfolio in portfolios:
        # Fetch account balances
        print("Evaluating %s" % portfolio)