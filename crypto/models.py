from __future__ import unicode_literals

from django.db import models
from common.core import view_link, edit_link
import scripting.models
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
    stamp   = models.DateTimeField('Start time')
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


# Back test
class Back_Test(models.Model):
    script = models.ForeignKey(scripting.models.Source, null=True, on_delete=models.SET_NULL)
    pair = models.ForeignKey(Pair, on_delete=models.SET_NULL, null=True)
    dt_start = models.DateTimeField('Start of test')
    dt_stop = models.DateTimeField('End of test')
    status = models.CharField('Activity status', max_length=64, default=BACK_TEST_READY)
    finished = models.BooleanField('Is finished?', default=True)
    error_msg = models.CharField('Error message', max_length=1024, default='')

    def __str__(self):
        return '%s on %s [%s-%s]' % (self.script, self.pair, self.dt_start, self.dt_stop)

    def to_form_fields(self):
        script_name = '' if self.script is None else str(self.script)
        currency_pair = '' if self.pair is None else self.pair.c1+'_'+self.pair.c2
        exchange = '' if self.pair is None else self.pair.exchange.name
        dt_start = self.dt_start if self.dt_start else timezone.now() - timedelta(days=31)
        dt_stop = self.dt_stop if self.dt_stop else timezone.now()
        return [
            {'label': 'Script', 'name': 'script', 'value': script_name},
            {'label': 'Currency Pair', 'name': 'pair', 'value': currency_pair},
            {'label': 'Exchange', 'name': 'exchange', 'value': exchange},
            {'label': 'Start Date', 'name': 'dt_start', 'value': dt_start.date()},
            {'label': 'Stop Date', 'name': 'dt_stop', 'value': dt_stop.date()},
            {'type': 'hidden', 'name': 'pk', 'value': self.pk}
        ]
