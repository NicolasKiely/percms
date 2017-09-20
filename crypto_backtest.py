import django
import sys
import os
import datetime
from django.utils import timezone

os.environ['DJANGO_SETTINGS_MODULE'] = 'percms.settings'
django.setup()

import scripting.models
import scripting.utils
import crypto.models
import crypto.runtime

exchange_name = 'Poloniex'

def to_tz(time_str):
    dt = datetime.datetime.strptime(time_str, '%Y-%m-%d')
    return timezone.make_aware(dt, timezone.get_current_timezone())

argc = len(sys.argv)
if argc<3:
    print 'Usage: python %s <cat:script#version> <currency pair> [start] [end]' % sys.argv[0]
    sys.exit(0)

t_start = to_tz(sys.argv[3]) if argc>3 else None
t_end = to_tz(sys.argv[4]) if argc>4 else None

# Get script
script, source = scripting.utils.get_script_by_name(sys.argv[1])

# Get currency pair
exc = crypto.models.Exchange.objects.get(name=exchange_name)
c1, c2 = sys.argv[2].split('_')
currencies = crypto.models.Pair.objects.get(c1=c1, c2=c2, exc=exc)

# Initialize runtime
runtime_factory = crypto.runtime.Runtime_Factory(currencies)
runtime_factory.load_data(t_start, t_end)

currency_1_amount = 1.0
currency_2_amount = 0.0

transfer_percentage = 1.0 - 0.0020

# Iterate over time
print 'Time\t% Growth\tPrice'
for i in range(0, runtime_factory.num_candles):
    # Evaluate strategy for i'th candlestick
    runtime = runtime_factory.runtime(i)
    exec(source.source)

    candle = runtime_factory.candles[i]

    if runtime.confidence > 90:
        # Calculate transfer from cur1 to cur2
        if runtime.signal == crypto.runtime.BUY_SIGNAL:
            #print 'Buy!'
            transfer = currency_1_amount
            currency_1_amount -= transfer
            currency_2_amount += transfer_percentage * (transfer / candle.p_close)
        elif runtime.signal == crypto.runtime.SELL_SIGNAL:
            #print 'Sell!'
            transfer = currency_2_amount
            currency_1_amount += transfer_percentage * (transfer * candle.p_close)
            currency_2_amount -= transfer
    
    print '%s\t%s\t%s' % (
        candle.stamp.strftime('%Y-%m-%d %H:%M'),
        (currency_1_amount + currency_2_amount*candle.p_close) - 1.0,
        candle.p_close
    )
