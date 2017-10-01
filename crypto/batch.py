import time
import sys
import traceback
from django.utils import timezone
from scripting.utils import get_script_by_name

from . import models
from . import utils
from . import runtime as crypto_runtime
from . import poloniex_api
import filemanager.utils



# Exception to log on backtest results page
class Backtest_Exception(Exception):
    pass


def pull_candle_data(polo, c1, c2, t_start, t_end):
    ''' Pulls candlestick data for given currency pair in time frame '''
    pair_name = c1+'_'+c2
    exc, _ = crypto.models.Exchange.objects.get_or_create(name='Poloniex')
    pair, _ = crypto.models.Pair.objects.get_or_create(c1=c1, c2=c2, exc=exc)
    period = 300
    data = polo.returnChartData(pair_name, start=t_start, end=t_end, period=period)
    for x in data:
        dt = datetime.datetime.fromtimestamp(x['date'])
        dtz = timezone.make_aware(dt, timezone.get_current_timezone())
        try:
            candle = crypto.models.Candle_Stick.objects.get(
                pair = pair, stamp = dtz
            )
        except crypto.models.Candle_Stick.DoesNotExist:
            candle = crypto.models.Candle_Stick(pair=pair, stamp=dtz)

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
    runtime_factory.load_data(backtest.dt_start, backtest.dt_stop)

    # Setup currencies
    currency_1_amount = 1.0
    currency_2_amount = 0.0
    transfer_percentage = 1.0 - 0.0020

    # Iterate over time
    fout.write('Time\t% Growth\tPrice\tSignal\n')
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
        if runtime.confidence > 90:
            # Calculate transfer from cur1 to cur2
            if runtime.signal == crypto_runtime.BUY_SIGNAL:
                # Buy
                buy_signal = 1
                transfer = currency_1_amount
                currency_1_amount -= transfer
                currency_2_amount += transfer_percentage * (transfer / candle.p_close)

            elif runtime.signal == crypto_runtime.SELL_SIGNAL:
                # Sell
                buy_signal = -1
                transfer = currency_2_amount
                currency_1_amount += transfer_percentage * (transfer * candle.p_close)
                currency_2_amount -= transfer
        
        fout.write('%s\t%s\t%s\t%s\n' % (
            candle.stamp.strftime('%Y-%m-%d %H:%M'),
            (currency_1_amount + currency_2_amount*candle.p_close) - 1.0,
            candle.p_close,
            buy_signal
        ))


def POST_backtest(currencies, exchange_name, script_name, dt_start, dt_stop):
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


def POST_poloniex_candles_pull(currencies, dt_start, dt_stop, api_key_name):
    ''' Handler for pulling down candlestick data for poloniex '''
    # Get api key
    try:
        api_key = models.API_Key.objects.get(name=api_key_name)
    except models.API_Key.DoesNotExist:
        print 'API key "%s" not found' % api_key_name
        return

    polo = crypto.poloniex_api.poloniex(api_key.key, api_key.secret)

    t_start = int(time.mktime(dt_start.timetuple()))
    t_end = t_start + day_count*(60*60*24)
