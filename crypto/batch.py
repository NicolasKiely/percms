# import time
# import sys
import traceback
# from django.utils import timezone
# import datetime
# import pandas as pd
import urllib2
# import decimal

from scripting.utils import get_script_by_name
from . import models
from . import utils
from . import runtime as crypto_runtime
from . import poloniex_api
from . import portfolio_evaluation
from . import backtest
from . import exchange_interface
import filemanager.utils
import scripting.utils


def run_backtest(backtest, fout, period=14400):
    """ Run backtest """
    # Initialize runtime
    runtime_factory = crypto_runtime.Runtime_Factory(backtest.pairs.all())
    runtime_factory.load_data(backtest.dt_start, backtest.dt_stop, period=period)

    # Setup initial postition values: all currency in base
    base_amount = 1.0
    transfer_rate = 1.0
    base_name = backtest.base_currency.symbol
    c_names = [p.c2 for p in backtest.pairs.all()]
    balances = {c: 0.0 for c in c_names}
    positions = {c: '....' for c in c_names}
    rates = {c: 1.0 for c in c_names}

    # 1 - transaction costs
    transfer_percentage = 1.0 - 0.0020

    # Iterate over time
    # Header: Time, Portfolio growth, Positions ... , Balances ...
    header = 'Time\t%%Growth\t%s\t%s\t%s\t%s\n' % (
        '\t'.join(['Pos_'+c for c in c_names]),
        '\t'.join(['Bal_'+c for c in c_names]),
        '\t'.join([base_name+'_'+c for c in c_names]),
        '\t'.join(['STOP_'+c for c in c_names])
    )
    fout.write(header)

    index_len = len(runtime_factory.df.index)
    for i in range(1, index_len):
        # Iterate over time period
        # Get time-truncated dataframe from dt_start to given time period
        runtime_factory.truncate_data(i)

        # Calculate positions
        for c_name in c_names:
            # Iterate over currencies
            try:
                global runtime
                runtime = runtime_factory.runtime(c_name)
                exec(backtest.script.source)
            except Exception as ex:
                trace = traceback.format_exc()
                raise backtest.Backtest_Exception('Script Exception: %s' % trace)

            candle = runtime.data.iloc[-1]
            candle_close = candle['close']
            rates[c_name] = candle_close
            if runtime.is_stoploss_enabled() and candle_close<runtime.get_stoploss():
                # Stoploss
                positions[c_name] = 'STOP'

            elif runtime.signal == 'LONG':
                positions[c_name] = 'LONG'

            elif runtime.signal == 'SELL':
                positions[c_name] = 'SELL'

            else:
                positions[c_name] = '....'

        # Act on position: sells first, then buys
        for c_name in c_names:
            # Handle sells
            p = positions[c_name]
            rate = rates[c_name]
            if not (p == 'STOP' or p == 'SELL'):
                continue
            # Sell back base currency
            transfer = balances[c_name]
            base_amount += transfer_percentage * (transfer * rate)
            balances[c_name] -= transfer
            runtime_factory.stoploss_enabled[c_name] = False
            runtime_factory.stoploss[c_name] = 0.0
            
        for c_name in c_names:
            # Handle buys
            p = positions[c_name]
            rate = rates[c_name]
            if p != 'LONG':
                continue
            # Buy using base currency
            transfer = base_amount * transfer_rate
            base_amount -= transfer
            balances[c_name] += transfer_percentage * (transfer / rate)

        total_portfolio = base_amount
        for c_name in c_names:
            total_portfolio += balances[c_name] * rates[c_name]

        fout.write('%s\t%s%%\t%s\t%s\t%s\t%s\n' % (
            runtime_factory.trunc_df.index[-1].strftime('%Y-%m-%d %H:%M:%S'),
            100.0 * (total_portfolio-1.0),
            '\t'.join([str(positions[c]) for c in c_names]),
            '\t'.join([str(balances[c]) for c in c_names]),
            '\t'.join([str(rates[c]) for c in c_names]),
            '\t'.join([str(runtime_factory.stoploss[c]) for c in c_names])
        ))


def POST_backtest(
        logger, base_currency, trade_currencies, exchange_name,
        script_name, dt_start, dt_stop, period=14400
    ):
    ''' Handler for backtest batch test

        base_currency:
            Currency to trade against (eg BTC)
        trade_currencies:
            Space-separated list of currencies to trade (commas okay)
        exchange_name:
            Name of exchange for data usage
        script_name:
            Name of script to run strategy on
        dt_start:
            Start time of simulation
        dt_stop:
            Stop time of sumulation
        period:
            Candlestick Period (default=14400)
    '''
    # Create new test record
    backtest = models.Back_Test(
        dt_start=dt_start, dt_stop=dt_stop,
        status=models.BACK_TEST_TESTING, finished=False,
        period=period
    )
    backtest.save()

    try:
        # Get script source to use
        if not script_name:
            raise backtest.Backtest_Exception('Script name not given')
        script, source = get_script_by_name(script_name)
        backtest.script = source

        # Get currency pair to use
        base, _ = models.Currency.objects.get_or_create(symbol=base_currency)
        backtest.base_currency = base

        # Get trade pairs
        for trade_currency in trade_currencies.split(' '):
            trade_name = trade_currency.strip(',')
            try:
                pair = utils.get_currency_pair(exchange_name, base.symbol, trade_name)
            except models.Pair.DoesNotExist:
                raise backtest.Backtest_Exception(
                    'Currency pair %s_%s not found' % (base.symbol, trade_name)
                )
            backtest.pairs.add(pair)

        backtest.save()

        # Iterate over trading pairs
        for pair in backtest.pairs.all():
            #pair = utils.get_currency_pair(exchange_name, c1, c2)

            # Open result file
            meta_file = filemanager.utils.create_file_record(
                category='crypto_backtest',
                file_name='test_'+str(backtest.pk),
                is_image=False
            )
            fpath = meta_file.get_file_path()
            backtest.results_file = meta_file
            
            # Run script on results file
            with open(fpath, 'w') as fout:
                run_backtest(backtest, fout, period=period)

            # Finis
            backtest.status=models.BACK_TEST_FINISHED

    except backtest.Backtest_Exception as ex:
        backtest.error_msg = str(ex)
        backtest.status=models.BACK_TEST_FAILED

    except Exception as ex:
        backtest.error_msg = 'Exception %s: %s' % (type(ex), traceback.format_exc())
        backtest.status=models.BACK_TEST_FAILED

    # Save results
    backtest.finished = True
    backtest.save()


def POST_poloniex_candles_update(logger, api_key_name=None):
    """ Handler for pulling down candlestick data from poloniex """
    interface = exchange_interface.Poloniex_Interface(api_key_name)
    interface.update_candles(logger)


def POST_bittrex_candles_update(logger):
    """ Handler for pulling down exchange candlestick data """
    interface = exchange_interface.Bittrex_Interface(None)
    interface.update_candles(logger)


def POST_debug_polo_account(logger, api_key_name, pair=None):
    """ Posts information about poloniex portfolio

    api_key_name:
        Account name
    pair (optional):
        Currency pair to list open orders and trade history
    """
    Poloniex = models.Exchange.objects.get(name='Poloniex')
    try:
        api_key = models.API_Key.objects.get(name=api_key_name)
    except models.API_Key.DoesNotExist:
        print 'API key "%s" not found' % api_key_name
        return

    polo = poloniex_api.poloniex(str(api_key.key), str(api_key.secret))
    balances = polo.returnBalances()

    # Print balance
    print 'Balance'
    for c, v in balances.iteritems():
        fv = float(v)
        if fv > 0:
            print '%s: %s' % (c, fv)

    if pair:
        # Print orders for pair
        print 'Open Orders:'
        print polo.returnOpenOrders(pair)

        print 'Trade History:'
        print polo.returnTradeHistory(pair)


def POST_manual_polo_trade(logger, api_key_name, pair, amount, trade='buy'):
    """ Place manual trade for an account

    api_key_name:
        Account name
    pair:
        Pair to trade
    amount:
        Amount to buy
    trade:
        "buy" or "sell" (defaults to "buy")
    """
    Poloniex = models.Exchange.objects.get(name='Poloniex')
    try:
        api_key = models.API_Key.objects.get(name=api_key_name)
    except models.API_Key.DoesNotExist:
        print 'API key "%s" not found' % api_key_name
        return
    polo = poloniex_api.poloniex(str(api_key.key), str(api_key.secret))
    ticker = polo.returnTicker()
    pair_ticker = ticker[pair]

    try:
        price = float(pair_ticker['last'])
        print price
        orders = polo.returnOpenOrders(pair)
        for order in orders:
            order_no = order['orderNumber']
            print 'Cancelling order #%s' % order_no
            print polo.cancel(pair, order_no)

        if trade.lower() != 'sell':
            q = polo.buy(str(pair), str(price*1.001), str(amount))
        else:
            q = polo.sell(str(pair), str(price*0.999), str(amount))
        print q

    except urllib2.HTTPError as ex:
        print 'HTTP error, buy failed'
        print str(ex) + ': ' + ex.read()

    except Exception as ex:
        print 'Buy failed'
        print ex


def POST_eval_portfolios(logger, commit='True'):
    """ Runs update on active portfolios """
    portfolios = models.Portfolio.objects.filter(active=True).all()
    Poloniex = models.Exchange.objects.get(name='Poloniex')

    do_commit = (commit.lower() == 'true')

    for portfolio in portfolios:
        logger.write('Portfolio %s' % portfolio)

        if portfolio.exc == Poloniex:
            logger.write('Poloniex exchange using account %s' % portfolio.key.name)
            portfolio_evaluation.eval_poloniex_portfolio(logger, portfolio, do_commit)
        else:
            interface = exchange_interface.get_interface(
                portfolio.exc.name, portfolio.key,
            )
            interface.eval_portfolio(logger, portfolio, commit)
