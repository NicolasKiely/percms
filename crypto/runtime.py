''' Runtime library for crypto trading '''
from . import models


class Runtime(object):
    ''' Stores argument information '''
    def __init__(self, currencies):
        self.revert_signal()
        self.currencies = currencies
        self.candles = None


    def load_data(self, t_start=None, t_end=None, period=300):
        ''' Loads data between time periods '''
        filter_args = {'period': period}
        if t_start: filter_args['stamp__gte']=t_start
        if t_end: filter_args['stamp__lt']=t_end
        self.candles = self.currencies.candle_stick_set.filter(
            **filter_args
        ).order_by('stamp').all()


    def revert_signal(self):
        ''' Resets buy/sell signal '''
        self.signal = ''
        self.confidence = 0


    def signal_buy(self, confidence):
        ''' Signals a buy, with an integer confidence between 0 and 100 '''
        self.signal = 'BUY'
        self.confidence = confidence


    def signal_sell(self, confidence):
        ''' Signals a sell, with an integer confidence between 0 and 100 '''
        self.signal = 'SELL'
        self.confidence = confidence
