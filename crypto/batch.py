from . import models
from django.utils import timezone

def POST_backtest(currencies, exchange, script_name, dt_start, dt_stop):
    #script, source = get_script_by_name(p['script'])
    backtest = models.Back_Test(
        dt_start=timezone.now(), dt_end=timezone.now(),
        status=models.BACK_TEST_FAILED, finished=True,
        error_msg='Testing backtest scripts, not fully implemented'
    )
    backtest.save()
