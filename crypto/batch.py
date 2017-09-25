from . import models
from . import utils
import time
from django.utils import timezone
from scripting.utils import get_script_by_name

class Backtest_Exception(Exception):
    pass


def POST_backtest(currencies, exchange_name, script_name, dt_start, dt_stop):
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

        backtest.error_msg = 'Testing backtest scripts, not fully implemented'
        backtest.status=models.BACK_TEST_FAILED

    except Backtest_Exception as ex:
        backtest.error_msg = str(ex)
        backtest.status=models.BACK_TEST_FAILED

    except Exception as ex:
        backtest.error_msg = 'Exception %s: %s' % (type(ex), str(ex))
        backtest.status=models.BACK_TEST_FAILED


    # Save results
    backtest.finished = True
    backtest.save()
