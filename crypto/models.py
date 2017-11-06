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


# Represents currency
class Currency(models.Model):
    symbol = models.CharField('Symbol of currency', max_length=16, unique=True)
    name = models.CharField('Optional descriptive name', max_length=255, null=True)

    

# Currency Pair at an exchange
class Pair(models.Model):
    c1 = models.CharField('First currency', max_length=16)
    c2 = models.CharField('Second currency', max_length=16)
    exc = models.ForeignKey(Exchange, on_delete=models.CASCADE)

    data_start = models.DateTimeField('Start date of contigous data pulled', null=True)
    data_stop = models.DateTimeField('End date of contigous data pulled', null=True)

    def __str__(self):
        return '[%s_%s %s]' % (self.c1, self.c2, self.exc.name[:3])

    class Meta:
        unique_together = ('c1', 'c2', 'exc')


# Represents investments in an exchange
class Wallet(models.Model):
    cash = models.FloatField('Free cash')


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
        unique_together = ('pair', 'stamp')


class Portfolio(models.Model):
    ''' Management of portfolio '''
    script = models.ForeignKey(scripting.models.Source, null=True, on_delete=models.SET_NULL)
    exc = models.ForeignKey(Exchange, on_delete=models.SET_NULL, null=True)
    base_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    key = models.ForeignKey(API_Key, on_delete=models.SET_NULL, null=True)
    pairs = models.ManyToManyField(Pair)
    active = models.BooleanField(default=False)
    last_eval = models.DateTimeField(null=True)

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
            {'type': 'checkbox', 'label': 'Active', 'name': 'active', 'value': self.active},
            {'type': 'hidden', 'name': 'pk', 'value': self.pk}
        ]

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

    def get_exchange_str(self):
        return self.exc.name if self.exc else 'Poloniex'

    def get_base_str(self):
        return self.base_currency.symbol if self.base_currency else 'USDT'

    def get_trade_str(self):
        try:
            return ' '.join([p.symbol for p in self.pairs.all()])
        except ValueError:
            return 'BTC'

    def get_start_str(self):
        #dt = self.dt_start if self.dt_start else timezone.now() - timedelta(days=31)
        dt = self.dt_start if self.dt_start else timezone.now() - timedelta(days=2)
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
            {'type': 'hidden', 'name': 'pk', 'value': self.pk}
        ]
