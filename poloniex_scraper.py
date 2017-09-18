import django
import os
import sys
import time
import datetime
from django.utils import timezone

os.environ['DJANGO_SETTINGS_MODULE'] = 'percms.settings'
django.setup()

import crypto.poloniex_api
import crypto.models


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


argc = len(sys.argv)
if argc < 2:
    print 'Usage: python %s <api key name> [Y-m-d] [# days]' % sys.argv[0]
    api_keys = crypto.models.API_Key.objects.all()
    if len(api_keys):
        print 'Available Keys:'
    for key in api_keys:
        print '\t"%s"' % key.name
    sys.exit(0)

if argc > 2:
    # Next arg is date to scrape
    scrape_date = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d')
else:
    scrape_date = None

day_count = int(sys.argv[3]) if argc>3 else 1


# Get api key
try:
    api_key = crypto.models.API_Key.objects.get(name=sys.argv[1])
except crypto.models.API_Key.DoesNotExist:
    print 'API key "%s" not found' % sys.argv[1]
    sys.exit(1)

polo = crypto.poloniex_api.poloniex(api_key.key, api_key.secret)

t_start = int(time.mktime(scrape_date.timetuple()))
t_end = t_start + day_count*(60*60*24)

#print '\n'.join(polo.returnTicker().keys())
#print '\n'.join( map(str, polo.returnMarketTradeHistory('BTC_ETH')))

pull_candle_data(polo, 'BTC', 'ETH', t_start, t_end)
