from __future__ import unicode_literals

from django.db import models
from common.core import view_link, edit_link
import scripting.models
from filemanager.models import Meta_File
from django.utils import timezone
from datetime import timedelta

BACK_TEST_READY = 'Ready'
BACK_TEST_TESTING = 'Testing'
BACK_TEST_FINISHED = 'Finished'
BACK_TEST_FAILED = 'Failed'


# Create your models here.
class API_Key(models.Model):
    name = models.CharField('Name of Key', max_length=256, unique=True)
    key = models.CharField('Key', max_length=4096)
    secret = models.CharField('Key secret', max_length=4096)

    def __str__(self):
        return self.name

    def edit_link(self):
        return edit_link('crypto:key_editor', (self.pk,), text='Edit Key')

    def view_link(self):
        return view_link('alerts:key_view', (self.pk,), text='View Key')

    def dashboard_link(self):
        url = reverse('alerts:key_dashboard')
        return '<a href="%s">Key Dashboard</a>' % url

    def to_form_fields(self):
        return [
            {'label': 'Name', 'name': 'name', 'value': self.name},
            {'label': 'Key', 'name': 'key', 'value': self.key},
            {'label': 'Secret', 'name': 'secret', 'value': self.secret},
            {'type': 'hidden', 'name': 'pk', 'value': self.pk}
        ]


class Exchange(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name

    def list_pairs(self):
        records = [] 
        for pair in self.pair_set.all():
            pair_str = pair.c1 +'_'+ pair.c2
            markers = pair.candle_marker_set.filter(active=True).all()
            if len(markers) == 0:
                continue
            period_str = ', '.join([
                str(marker.period)
                for marker in pair.candle_marker_set.filter(active=True).all()
            ])
            records.append(pair_str +': '+ period_str)

        return '\n'.join(records)

    def to_form_fields(self):
        return [
            {'label': 'Name', 'name': 'name', 'value': self.name},
            {
                'label': 'Tracked Pairs', 'type': 'area',
                'name': 'pairs', 'value': self.list_pairs()
            },
            {'type': 'hidden', 'name': 'pk', 'value': self.pk}
        ]


# Represents currency
class Currency(models.Model):
    symbol = models.CharField('Symbol of currency', max_length=16, unique=True)
    name = models.CharField('Optional descriptive name', max_length=255, null=True)

    

# Currency Pair at an exchange
class Pair(models.Model):
    c1 = models.CharField('First currency', max_length=16)
    c2 = models.CharField('Second currency', max_length=16)
    exc = models.ForeignKey(Exchange, on_delete=models.CASCADE)

    def name(self):
        return self.c1 +'_'+ self.c2

    def __str__(self):
        return '[%s_%s %s]' % (self.c1, self.c2, self.exc.name[:3])

    class Meta:
        unique_together = ('c1', 'c2', 'exc')


# Represents investments in an exchange
class Wallet(models.Model):
    cash = models.FloatField('Free cash')


class Candle_Marker(models.Model):
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    period  = models.IntegerField('Period in seconds')
    data_start = models.DateTimeField('Start date of contigous data pulled', null=True)
    data_stop = models.DateTimeField('End date of contigous data pulled', null=True)

    def __str__(self):
        a = '[x]' if self.active else '[ ]'
        return '%s %s: %s' % (a, self.pair, self.period)
    

# Candlestick data
class Candle_Stick(models.Model):
    pair    = models.ForeignKey(Pair, on_delete=models.CASCADE)
    stamp   = models.DateTimeField('Start time', db_index=True)
    p_high  = models.FloatField('High')
    p_low   = models.FloatField('Low')
    p_close = models.FloatField('Close')
    p_open  = models.FloatField('Open')
    volume  = models.FloatField('Volume')
    q_volume = models.FloatField('Quoted Volume')
    w_average = models.FloatField('Weighted Average')
    period  = models.IntegerField('Period in seconds')


    def is_hollow(self): return self.p_close > self.p_open
    def is_filled(self): return self.p_close <= self.p_open

    def data_dict(self):
        return {
            'p_high': self.p_high,
            'p_low': self.p_low,
            'p_close': self.p_close,
            'p_open': self.p_open,
            'volume': self.volume,
            'q_volume': self.q_volume,
            'w_average': self.w_average,
        }

    def __str__(self):
        return '<%s %s: o=%s c=%s l=%s h=%s v=%s qv=%s wa=%s p=%s>' % (
            self.pair, self.stamp,
            self.p_open, self.p_close,
            self.p_low, self.p_high,
            self.volume, self.q_volume,
            self.w_average,
            self.period
        )

    class Meta:
        unique_together = ('pair', 'stamp', 'period')


class Portfolio(models.Model):
    ''' Management of portfolio '''
    script = models.ForeignKey(scripting.models.Source, null=True, on_delete=models.SET_NULL)
    exc = models.ForeignKey(Exchange, on_delete=models.SET_NULL, null=True)
    base_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    key = models.ForeignKey(API_Key, on_delete=models.SET_NULL, null=True)
    pairs = models.ManyToManyField(Pair)
    active = models.BooleanField(default=False)
    last_eval = models.DateTimeField(null=True)
    period = models.IntegerField('Candle Freq', default=14400)
    position_limit = models.FloatField('% of portfolio to commit', default=1.0)
    buy_limit = models.FloatField('% of portfolio to buy at a time', default=1.0)

    def get_exchange_str(self):
        return self.exc.name if self.exc else ''

    def get_base_str(self):
        return self.base_currency.symbol if self.base_currency else ''

    def get_trade_str(self):
        try:
            return ' '.join([p.c2 for p in self.pairs.all()])
        except ValueError:
            return ''

    def get_script_str(self):
        if self.script:
            return str(self.script)
        else:
            return ''

    def __str__(self):
        return '%s on %s' % (self.script, self.get_base_str())

    def get_api_key(self):
        if self.key:
            return self.key.name
        else:
            return ''

    def to_form_fields(self):
        return [
            {'label': 'Script', 'name': 'script', 'value': self.get_script_str()},
            {'label': 'Exchange', 'name': 'exchange', 'value': self.get_exchange_str()},
            {'label': 'API Key', 'name': 'key', 'value': self.get_api_key()},
            {'label': 'Base Currency', 'name': 'base', 'value': self.get_base_str()},
            {'label': 'Trade Currencies', 'name': 'trade', 'value': self.get_trade_str()},
            {'label': 'Frequency', 'name': 'period', 'value': self.period},
            {'label': 'Position Limit', 'name': 'pos_limit', 'value': self.position_limit},
            {'label': 'Buy Limit', 'name': 'buy_limit', 'value': self.buy_limit},
            {'type': 'checkbox', 'label': 'Active', 'name': 'active', 'value': self.active},
            {'type': 'hidden', 'name': 'pk', 'value': self.pk}
        ]


class Portfolio_History(models.Model):
    ''' Value of portfolio at given time '''
    stamp   = models.DateTimeField('Start time', db_index=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    base_holding = models.FloatField('Amount of base currency held')
    total_holding = models.FloatField('Total portfolio value relative to base currency')
    

class Portfolio_Position_History(models.Model):
    ''' Value of a currency pair position of a portfolio at a given time '''
    history = models.ForeignKey(Portfolio_History, on_delete=models.CASCADE)
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)

    amount_held = models.FloatField('Amount of currency held')
    value_held = models.FloatField('Value of holding wrt base currency')

    class Meta:
        unique_together = ('history', 'pair')


# Represents a position for a portfolio
class Portfolio_Position(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    position = models.CharField('Position on pair', max_length=32, null=True, default='....')
    stoploss = models.FloatField('Stoploss value', null=True)

    def __str__(self):
        return '[%s %s : %s]' % (self.pair.exc.name, self.pair.name(), self.position)

    class Meta:
        unique_together = ('portfolio', 'pair')


# Back test
class Back_Test(models.Model):
    script = models.ForeignKey(scripting.models.Source, null=True, on_delete=models.SET_NULL)
    exc = models.ForeignKey(Exchange, on_delete=models.SET_NULL, null=True)
    base_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    pairs = models.ManyToManyField(Pair)
    dt_start = models.DateTimeField('Start of test')
    dt_stop = models.DateTimeField('End of test')
    status = models.CharField('Activity status', max_length=64, default=BACK_TEST_READY)
    finished = models.BooleanField('Is finished?', default=True)
    error_msg = models.CharField('Error message', max_length=1024, default='')
    results_file = models.ForeignKey(Meta_File, on_delete=models.SET_NULL, null=True)
    period = models.IntegerField('Candle Freq', default=14400)

    def get_exchange_str(self):
        return self.exc.name if self.exc else 'Poloniex'

    def get_base_str(self):
        return self.base_currency.symbol if self.base_currency else 'BTC'

    def get_trade_str(self):
        try:
            return ' '.join([p.symbol for p in self.pairs.all()])
        except ValueError:
            return 'ETH'

    def get_start_str(self):
        #dt = self.dt_start if self.dt_start else timezone.now() - timedelta(days=31)
        dt = self.dt_start if self.dt_start else timezone.now() - timedelta(days=31)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def get_stop_str(self):
        dt = self.dt_stop if self.dt_stop else timezone.now()
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def get_script_str(self):
        if self.script:
            return str(self.script)
        else:
            try:
                script = Back_Test.objects.order_by('-pk')[0:1].get().script
                return str(script.script) if script else ''
            except Back_Test.DoesNotExist:
                return ''


    def __str__(self):
        return '%s on %s [%s - %s]' % (
            self.script, self.get_base_str(),
            self.get_start_str(), self.get_stop_str()
        )

    def to_form_fields(self):
        return [
            {'label': 'Script', 'name': 'script', 'value': self.get_script_str()},
            {'label': 'Exchange', 'name': 'exchange', 'value': self.get_exchange_str()},
            {'label': 'Base Currency', 'name': 'base', 'value': self.get_base_str()},
            {'label': 'Trade Currencies', 'name': 'trade', 'value': self.get_trade_str()},
            {'label': 'Start Date', 'name': 'dt_start', 'value': self.get_start_str()},
            {'label': 'Stop Date', 'name': 'dt_stop', 'value': self.get_stop_str()},
            {'label': 'Frequency', 'name': 'period', 'value': self.period},
            {'type': 'hidden', 'name': 'pk', 'value': self.pk}
        ]
