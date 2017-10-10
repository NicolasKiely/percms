import time
import sys
import traceback
from django.utils import timezone
import datetime
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
    runtime_factory = crypto_runtime.Runtime_Factory(backtest.pair)
    runtime_factory.load_data(backtest.dt_start, backtest.dt_stop, period=14400)

    # Setup currencies
    currency_1_amount = 1.0
    currency_2_amount = 0.0
    transfer_percentage = 1.0 - 0.0020

    # Iterate over time
    fout.write('Time\t% Growth\tPrice\tSignal\tStoploss\n')
    for i in range(0, runtime_factory.num_candles):
        # Evaluate strategy for i'th candlestick
        try:
            global runtime
            runtime = runtime_factory.runtime(i)
            exec(backtest.script.source)
        except Exception as ex:
            trace = traceback.format_exc()
            raise Backtest_Exception('Script Exception: %s' % trace)

        candle = runtime_factory.candles[i]

        buy_signal = 0
        if runtime_factory.stoploss_enabled and candle.p_close < runtime_factory.stoploss:
            # Stoploss
            buy_signal = -2

        elif runtime.confidence > 90:
            # Calculate transfer from cur1 to cur2
            if runtime.signal == crypto_runtime.BUY_SIGNAL:
                # Buy
                buy_signal = 1

            elif runtime.signal == crypto_runtime.SELL_SIGNAL:
                # Sell
                buy_signal = -1

        if buy_signal > 0:
            # Buy
            transfer = currency_1_amount
            currency_1_amount -= transfer
            currency_2_amount += transfer_percentage * (transfer / candle.p_close)

        elif buy_signal < 0:
            # Sell
            transfer = currency_2_amount
            currency_1_amount += transfer_percentage * (transfer * candle.p_close)
            currency_2_amount -= transfer
            runtime_factory.stoploss_enabled = False
            runtime_factory.stoploss = 0
        
        fout.write('%s\t%s\t%s\t%s\t%s\n' % (
            candle.stamp.strftime('%Y-%m-%d %H:%M'),
            (currency_1_amount + currency_2_amount*candle.p_close) - 1.0,
            candle.p_close,
            buy_signal,
            runtime_factory.stoploss
        ))


def POST_backtest(logger, currencies, exchange_name, script_name, dt_start, dt_stop):
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
        c1, c2 = currencies.split('_')
        pair = utils.get_currency_pair(exchange_name, c1, c2)
        backtest.pair = pair

        meta_file = filemanager.utils.create_file_record(
            category='crypto_backtest',
            file_name='test_'+str(backtest.pk),
            is_image=False
        )
        fpath = meta_file.get_file_path()
        backtest.results_file = meta_file
        with open(fpath, 'w') as fout:
            run_backtest(backtest, fout)

        backtest.status=models.BACK_TEST_FINISHED

    except Backtest_Exception as ex:
        backtest.error_msg = str(ex)
        backtest.status=models.BACK_TEST_FAILED

    except Exception as ex:
        backtest.error_msg = 'Exception %s: %s' % (type(ex), str(ex))
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
        # TODO: calculate t_start t_stop
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

