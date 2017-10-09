''' Runtime library for crypto trading '''
from . import models

BUY_SIGNAL = 'BUY'
SELL_SIGNAL = 'SELL'


class Runtime(object):
    ''' Stores argument information '''
    def __init__(self, factory, data):
        self.signal = ''
        self.confidence = 0
        self.data = data
        self.factory = factory

    def set_time(self, stamp):
        ''' Sets current time '''
        self.stamp = stamp


    def signal_buy(self, confidence=100):
        ''' Signals a buy, with an integer confidence between 0 and 100 '''
        self.signal = BUY_SIGNAL
        self.confidence = confidence


    def set_stoploss(self, stoploss, use_max=True):
        ''' Enables stoploss '''
        self.factory.stoploss_enabled = True
        if (use_max and stoploss > self.factory.stoploss) or not(use_max):
            self.factory.stoploss = stoploss


    def update_stoploss(self, stoploss, use_max=True):
        ''' Update stoploss if enabled '''
        if self.factory.stoploss_enabled:
            if (use_max and stoploss > self.factory.stoploss) or not(use_max):
                self.factory.stoploss = stoploss


    def signal_sell(self, confidence=100):
        ''' Signals a sell, with an integer confidence between 0 and 100 '''
        self.signal = SELL_SIGNAL
        self.confidence = confidence


class Runtime_Factory(object):
    def __init__(self, currencies):
        self.currencies = currencies
        self.candles = None
        self.num_candles = 0
        self.stoploss = 0
        self.stoploss_enabled = False


    def load_data(self, t_start=None, t_end=None, period=300):
        ''' Loads data between time periods '''
        filter_args = {'period': period}
        if t_start: filter_args['stamp__gte']=t_start
        if t_end: filter_args['stamp__lt']=t_end
        self.candles = self.currencies.candle_stick_set.filter(
            **filter_args
        ).order_by('stamp').all()[:]
        self.num_candles = len(self.candles)


    def runtime(self, i):
        return Runtime(self, self.candles[:i])
