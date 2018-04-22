import datetime
import time
import bittrex.bittrex as btrx
from django.utils import timezone
from . import models


# Bittrex period lookup from second count to api constant
BITTREX_PERIODS = {
    60: btrx.TICKINTERVAL_ONEMIN,
    300: btrx.TICKINTERVAL_FIVEMIN,
    1800: btrx.TICKINTERVAL_THIRTYMIN,
    3600: btrx.TICKINTERVAL_HOUR
}


def pulling_date_chunk_size(period):
    ''' Returns number of days to pull data from in one chunk '''
    return int(period)/30


def fetch_candle_data(polo, c1_c2, scrape_start, scrape_stop, period):
    ''' Fetches candlestick period data between given datetimes for currencies '''
    t_int_start = int(time.mktime(scrape_start.timetuple()))
    t_int_end = int(time.mktime(scrape_stop.timetuple()))
    return polo.returnChartData(c1_c2, start=t_int_start, end=t_int_end, period=period)


def save_polo_candle_data(polo, c1, c2, period, data):
    ''' Pulls candlestick data for given currency pair in time frame '''
    exc, _ = models.Exchange.objects.get_or_create(name='Poloniex')
    pair, _ = models.Pair.objects.get_or_create(c1=c1, c2=c2, exc=exc)

    candle_objs = []

    try:
        max_id = models.Candle_Stick.objects.order_by('-id')[0].id
    except IndexError:
        max_id = 0

    for x in data:
        dt = datetime.datetime.fromtimestamp(x['date'])
        dtz = timezone.make_aware(dt, timezone.get_current_timezone())
        try:
            candle = models.Candle_Stick.objects.get(
                pair = pair, stamp = dtz, period = period
            )
            created = False
            old_data = candle.data_dict()

        except models.Candle_Stick.DoesNotExist:
            candle = models.Candle_Stick(pair=pair, stamp=dtz, period=period)
            created = True

        candle.p_high    = x['high']
        candle.p_low     = x['low']
        candle.p_close   = x['close']
        candle.p_open    = x['open']
        candle.volume    = x['volume']
        candle.q_volume  = x['quoteVolume']
        candle.w_average = x['weightedAverage']
        candle.period    = period
        if created:
            max_id += 1
            candle.id = max_id
            candle_objs.append(candle)
        else:
            new_data = candle.data_dict()
            changed = False
            for k, v in old_data.iteritems():
                if v != new_data[k]:
                    changed = True
            if changed:
                candle.save()

    models.Candle_Stick.objects.bulk_create(candle_objs)


def update_bittrex(logger, bittrex):
    exc = models.Exchange.objects.get(name='Bittrex')
    pairs = exc.pair_set.all()
    #pair_names = [p.c1+'-'+p.c2 for p in pairs]

    markers = []
    for pair in pairs:
        for marker in pair.candle_marker_set.filter(active=True).all():
            markers.append(marker)

    #for pair in pair_names:
    for marker in markers:
        period = marker.period
        time = BITTREX_PERIODS[marker.period] # Get time period from pair
        pair = marker.pair
        pair_name = pair.c1 +'-'+ pair.c2
        candles = bittrex.get_candles(pair_name, time)['result']

        candle_objs = []
        max_id = models.Candle_Stick.objects.order_by('-id')[0].id
        for x in candles:
            # Format: {'C':#, 'H':#, 'L':#, 'O':#, 'BV':#, 'T':#', 'V':#}
            dt = datetime.datetime.strptime(x['T'], '%Y-%m-%dT%H:%M:%S')
            dtz = timezone.make_aware(dt, timezone.get_current_timezone())

            try:
                candle = models.Candle_Stick.objects.get(
                    pair = pair, stamp = dtz, period = period
                )
                created = False
                old_data = candle.data_dict()

            except models.Candle_Stick.DoesNotExist:
                candle = models.Candle_Stick(pair=pair, stamp=dtz, period=period)
                created = True
            candle.p_high    = x['H']
            candle.p_low     = x['L']
            candle.p_close   = x['C']
            candle.p_open    = x['O']
            candle.volume    = x['V']
            candle.q_volume  = 0
            candle.w_average = 0
            candle.period    = period
            if created:
                max_id += 1
                candle.id = max_id
                candle_objs.append(candle)
            else:
                new_data = candle.data_dict()
                changed = False
                for k, v in old_data.iteritems():
                    if v != new_data[k]:
                        changed = True
                if changed:
                    candle.save()

        logger.write('Currency '+ pair_name +' processed for Bittrex')
        models.Candle_Stick.objects.bulk_create(candle_objs)


def update_poloniex(logger, polo):
    # Get list of currency pairs
    exc = models.Exchange.objects.get(name='Poloniex')
    markers = []
    for pair in exc.pair_set.all():
        for marker in pair.candle_marker_set.filter(active=True).all():
            markers.append(marker)

    log_messages = []
    for marker in markers:
        period = marker.period
        pair = marker.pair
        c1 = pair.c1
        c2 = pair.c2
        messages = ['Period=%s, Pair=%s_%s' % (period, c1, c2)]
        profile_start = time.time()

        # Check if any data has been pulled for this currency
        if marker.data_stop == None:
            # No end date, start from beginning
            if marker.data_start == None:
                # No initial date, search for beginning
                messages.append(
                    'No initial date detected, initializing search for beginning'
                )
                marker.data_start = datetime.datetime(2012, 01, 01)
            else:
                messages.append(
                    'No end date detected, continuing search for beginning'
                )

            days_ahead = pulling_date_chunk_size(period)
            end_date = marker.data_start + datetime.timedelta(days_ahead)
            messages.append(
                'Looking at time frame %s to %s' % (marker.data_start, end_date)
            )

            # Try to pull data
            data = fetch_candle_data(
                polo, c1+'_'+c2, marker.data_start, end_date, int(period)
            )
            profile_fetch = time.time()
            messages.append(
                'Download time: %0.2fs' % (profile_fetch - profile_start)
            )

            if len(data) < 1 or data[0]['date'] == 0:
                # No data, continue on
                messages.append('No data in this time period')
                marker.data_start = end_date
                time.sleep(0.25)

            else:
                # First data set found
                messages.append('Data size: '+ str(len(data)))
                save_polo_candle_data(polo, c1, c2, int(period), data)
                profile_save = time.time()
                messages.append(
                    'Processing time: %0.2fs' % (profile_save - profile_fetch)
                )
                dt = datetime.datetime.fromtimestamp(data[0]['date'])
                dtz = timezone.make_aware(dt, timezone.get_current_timezone())
                marker.data_start = dtz
                dt = datetime.datetime.fromtimestamp(data[-1]['date'])
                dtz = timezone.make_aware(dt, timezone.get_current_timezone())
                marker.data_stop = dtz
            marker.save()

        else:
            # Continue on scraping
            start_date = marker.data_stop
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

            profile_fetch = time.time()
            messages.append(
                'Download time: %0.2fs' % (profile_fetch - profile_start)
            )

            if len(data) < 1 or data[0]['date'] == 0:
                messages.append('No data in this time period')
            else:
                messages.append('Data: '+ str(len(data)))
                save_polo_candle_data(polo, c1, c2, int(period), data)
                profile_save = time.time()
                messages.append(
                    'Processing time: %0.2fs' % (profile_save - profile_fetch)
                )
                dt = datetime.datetime.fromtimestamp(data[-1]['date'])
                dtz = timezone.make_aware(dt, timezone.get_current_timezone())
                marker.data_stop = dtz

            marker.save()
        
        log_messages.append('\n'.join(messages))
        logger.write('Currency '+c1+'_'+c2+' processed for Poloniex')
    logger.log('Candle Scraper Testing', '\n\n'.join(log_messages))
    logger.write('\n')
