''' Runtime library for crypto trading '''
from . import models

BUY_SIGNAL = 'BUY'
SELL_SIGNAL = 'SELL'


class Runtime(object):
    ''' Stores argument information '''
    def __init__(self, data):
        self.signal = ''
        self.confidence = 0
        self.data = data

    def set_time(self, stamp):
        ''' Sets current time '''
        self.stamp = stamp


    def signal_buy(self, confidence=100):
        ''' Signals a buy, with an integer confidence between 0 and 100 '''
        self.signal = BUY_SIGNAL
        self.confidence = confidence


    def signal_sell(self, confidence=100):
        ''' Signals a sell, with an integer confidence between 0 and 100 '''
        self.signal = SELL_SIGNAL
        self.confidence = confidence


class Runtime_Factory(object):
    def __init__(self, currencies):
        self.currencies = currencies
        self.candles = None
        self.num_candles = 0


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
        return Runtime(self.candles[:i])
