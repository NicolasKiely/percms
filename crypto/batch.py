import time
import sys
import traceback
from django.utils import timezone
import datetime
import pandas as pd

from scripting.utils import get_script_by_name
from . import models
from . import utils
from . import runtime as crypto_runtime
from . import poloniex_api
import filemanager.utils
import scripting.utils


def pulling_date_chunk_size(period):
    ''' Returns number of days to pull data from in one chunk '''
    return int(period)/30


# Exception to log on backtest results page
class Backtest_Exception(Exception):
    pass


def fetch_candle_data(polo, c1_c2, scrape_start, scrape_stop, period):
    ''' Fetches candlestick period data between given datetimes for currencies '''
    t_int_start = int(time.mktime(scrape_start.timetuple()))
    t_int_end = int(time.mktime(scrape_stop.timetuple()))
    return polo.returnChartData(c1_c2, start=t_int_start, end=t_int_end, period=period)


def save_candle_data(polo, c1, c2, period, data):
    ''' Pulls candlestick data for given currency pair in time frame '''
    exc, _ = models.Exchange.objects.get_or_create(name='Poloniex')
    pair, _ = models.Pair.objects.get_or_create(c1=c1, c2=c2, exc=exc)
    for x in data:
        dt = datetime.datetime.fromtimestamp(x['date'])
        dtz = timezone.make_aware(dt, timezone.get_current_timezone())
        try:
            candle = models.Candle_Stick.objects.get(
                pair = pair, stamp = dtz
            )
        except models.Candle_Stick.DoesNotExist:
            candle = models.Candle_Stick(pair=pair, stamp=dtz)

        candle.p_high    = x['high']
        candle.p_low     = x['low']
        candle.p_close   = x['close']
        candle.p_open    = x['open']
        candle.volume    = x['volume']
        candle.q_volume  = x['quoteVolume']
        candle.w_average = x['weightedAverage']
        candle.period    = period
        candle.save()


def run_backtest(backtest, fout):
    ''' Run backtest '''
    # Initialize runtime
    runtime_factory = crypto_runtime.Runtime_Factory(backtest.pairs.all())
    runtime_factory.load_data(backtest.dt_start, backtest.dt_stop, period=14400)

    # Setup initial postition values: all currency in base
    base_amount = 1.0
    base_name = backtest.base_currency.symbol
    c_names = [p.c2 for p in backtest.pairs.all()]
    balances = {c: 0.0 for c in c_names}
    positions = {c: '....' for c in c_names}
    rates = {c: 1.0 for c in c_names}

    # 1 - transaction costs
    transfer_percentage = 1.0 - 0.0020

    # Iterate over time
    # Header: Time, Portfolio growth, Positions ... , Balances ...
    header = 'Time\t%%Growth\t%s\t%s\t%s\n' % (
        '\t'.join(['Pos_'+c for c in c_names]),
        '\t'.join(['Bal_'+c for c in c_names]),
        '\t'.join([base_name+'_'+c for c in c_names])
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
                raise Backtest_Exception('Script Exception: %s' % trace)

            candle = runtime.data.iloc[-1]
            rates[c_name] = candle['close']
            if runtime.is_stoploss_enabled() and p_close<runtime.get_stoploss():
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
            if p != 'STOP' and p != 'SELL':
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
            transfer = base_amount
            base_amount -= transfer
            balances[c_name] += transfer_percentage * (transfer / rate)

        total_portfolio = base_amount
        for c_name in c_names:
            total_portfolio += balances[c_name] * rates[c_name]

        fout.write('%s\t%s%%\t%s\t%s\t%s\n' % (
            runtime_factory.trunc_df.index[-1].strftime('%Y-%m-%d %H:%M:%S'),
            100.0 * (total_portfolio-1.0),
            '\t'.join([str(positions[c]) for c in c_names]),
            '\t'.join([str(balances[c]) for c in c_names]),
            '\t'.join([str(rates[c]) for c in c_names])
        ))


def POST_backtest(
        logger, base_currency, trade_currencies, exchange_name,
        script_name, dt_start, dt_stop
    ):
    ''' Handler for backtest batch test '''
    # Create new test record
    backtest = models.Back_Test(
        dt_start=dt_start, dt_stop=dt_stop,
        status=models.BACK_TEST_TESTING, finished=False
    )
    backtest.save()

    try:
        # Get script source to use
        if not script_name:
            raise Backtest_Exception('Script name not given')
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
                raise Backtest_Exception(
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
                run_backtest(backtest, fout)

            # Finis
            backtest.status=models.BACK_TEST_FINISHED

    except Backtest_Exception as ex:
        backtest.error_msg = str(ex)
        backtest.status=models.BACK_TEST_FAILED

    except Exception as ex:
        backtest.error_msg = 'Exception %s: %s' % (type(ex), traceback.format_exc())
        backtest.status=models.BACK_TEST_FAILED


    # Save results
    backtest.finished = True
    backtest.save()


def POST_poloniex_candles_update(logger, api_key_name, period):
    ''' Handler for pulling down candlestick data from poloniex for 5min, 4hr, 1d

    5 min  = 300
    1 hour = 3600
    4 hour = 14400
    1 day  = 86400
    '''
    # Get api key
    try:
        api_key = models.API_Key.objects.get(name=api_key_name)
    except models.API_Key.DoesNotExist:
        logger.log('API Key Error', 'API Key "%s" not found' % api_key_name)
        return

    polo = poloniex_api.poloniex(api_key.key, api_key.secret)

    # Get list of currency pairs
    exc = models.Exchange.objects.get(name='Poloniex')
    for c1, c2 in poloniex_api.USDT_PAIRS:
        messages = ['Period=%s, Pair=%s_%s' % (period, c1, c2)]

        # Check if any data has been pulled for this currency
        pair, _ = models.Pair.objects.get_or_create(exc=exc, c1=c1, c2=c2)
        if pair.data_stop == None:
            # No end date, start from beginning
            if pair.data_start == None:
                # No initial date, search for beginning
                messages.append(
                    'No initial date detected, initializing search for beginning'
                )
                pair.data_start = datetime.datetime(2012, 01, 01)
            else:
                messages.append(
                    'No end date detected, continuing search for beginning'
                )
            days_ahead = pulling_date_chunk_size(period)
            end_date = pair.data_start + datetime.timedelta(days_ahead)
            messages.append(
                'Looking at time frame %s to %s' % (pair.data_start, end_date)
            )

            # Try to pull data
            data = fetch_candle_data(
                polo, c1+'_'+c2, pair.data_start, end_date, int(period)
            )
            if len(data) < 1 or data[0]['date'] == 0:
                # No data, continue on
                messages.append('No data in this time period')
                pair.data_start = end_date

            else:
                # First data set found
                messages.append('Data: '+ ''.join(['\n\t'+str(d) for d in data]))
                save_candle_data(polo, c1, c2, int(period), data)
                pair.data_stop = end_date

            pair.save()

        else:
            # Continue on scraping
            start_date = pair.data_stop
            if start_date > timezone.now():
                start_date = timezone.now() - datetime.timedelta(1)
            days_ahead = pulling_date_chunk_size(period)
            end_date = start_date + datetime.timedelta(days_ahead)

            messages.append(
                'Looking at time frame %s to %s' % (start_date, end_date)
            )

            data = fetch_candle_data(
                polo, c1+'_'+c2, start_date, end_date, int(period)
            )
            if len(data) < 1 or data[0]['date'] == 0:
                messages.append('No data in this time period')
            else:
                messages.append('Data: '+ ''.join(['\n\t'+str(d) for d in data]))
                save_candle_data(polo, c1, c2, int(period), data)
                pair.data_stop = end_date

            pair.save()
        
        logger.log('Candle Scraper Testing', '\n'.join(messages))
        logger.write('Currency '+c1+'_'+c2+' processed')


def POST_poloniex_candles_pull(logger, currencies, dt_start, dt_stop, api_key_name, period):
    ''' Handler for pulling down candlestick data for poloniex '''
    # Get api key
    try:
        api_key = models.API_Key.objects.get(name=api_key_name)
    except models.API_Key.DoesNotExist:
        print 'API key "%s" not found' % api_key_name
        return

    polo = poloniex_api.poloniex(api_key.key, api_key.secret)

    exchange_name = 'Poloniex'
    c1, c2 = currencies.split('_')

    scrape_start = datetime.datetime.strptime(dt_start, '%Y-%m-%d')
    scrape_stop = datetime.datetime.strptime(dt_stop, '%Y-%m-%d')
    
    p = int(period)
    data = fetch_candle_data(polo, currencies, scrape_start, scrape_stop, p)
    save_candle_data(polo, c1, c2, p, data)

