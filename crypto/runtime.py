''' Runtime library for crypto trading '''
from . import models
import pandas as pd

NO_SIGNAL   = '....'
BUY_SIGNAL  = 'LONG'
SELL_SIGNAL = 'SELL'
STOP_SIGNAL = 'STOP'


class Runtime(object):
    ''' Provides API for strategy scripts to get data and output signals

    Data Format is pandas dataframe:
        index: time
        columns: close, high, low, volume
    '''
    def __init__(self, factory, name, data):
        self.name = name
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
        self.factory.stoploss_enabled[self.name] = True
        if (use_max and stoploss > self.get_stoploss()) or not(use_max):
            self.factory.stoploss[self.name] = stoploss

    def update_stoploss(self, stoploss, use_max=True):
        ''' Update stoploss if enabled '''
        if self.is_stoploss_enabled():
            if (use_max and stoploss > self.get_stoploss()) or not(use_max):
                self.factory.stoploss[self.name] = stoploss

    def signal_sell(self, confidence=100):
        ''' Signals a sell, with an integer confidence between 0 and 100 '''
        self.signal = SELL_SIGNAL
        self.confidence = confidence

    def get_stoploss(self):
        return self.factory.stoploss[self.name]

    def is_stoploss_enabled(self):
        return self.factory.stoploss_enabled[self.name]


class Runtime_Factory(object):
    def __init__(self, currency_pairs):
        # List of currency pair objects
        self.pairs = currency_pairs

        # Raw currency pair: candle time series data
        self.candles = {}

        # Currency Pair: Stoploss values
        self.stoploss = {c.c2:0 for c in currency_pairs}

        # Currency Pair: Stoploss enabled flags
        self.stoploss_enabled = {c.c2: False for c in currency_pairs}

        # Central data frame, indexed by timestamp and columns of:
        # X_close, X_high, X_low, X_volume for x currency pair symbols
        self.df = None

        # Data frame limitted up to given index
        self.trunc_df = None

    def truncate_data(self, i):
        ''' Build truncated dataframe '''
        self.trunc_df = self.df.iloc[:i+1]

    def load_data(self, t_start=None, t_end=None, period=300):
        ''' Loads data between time periods '''
        filter_args = {'period': period}
        if t_start: filter_args['stamp__gte']=t_start
        if t_end: filter_args['stamp__lt']=t_end

        df_list = []

        for pair in self.pairs:
            name = pair.c2
            candles = pair.candle_stick_set.filter(
                **filter_args
            ).order_by('stamp').all()[:]
            if len(candles) == 0:
                continue

            candles_df = pd.DataFrame({
                name+'_open': [c.p_open for c in candles],
                name+'_close': [c.p_close for c in candles],
                name+'_high': [c.p_high for c in candles],
                name+'_low': [c.p_low for c in candles],
                name+'_volume': [c.volume for c in candles]
            }, index = [c.stamp for c in candles])
            df_list.append(candles_df)
            self.candles[pair.c2] = candles
            
        try:
            self.df = pd.concat(df_list, axis=1)
        except TypeError as ex:
            with open("temp.txt", "w") as fh:
                fh.write('\n\n'.join(map(str, df_list)))
                raise ex

    def runtime(self, c_name):
        ''' Build runtime at time i '''
        df = self.df if self.trunc_df is None else self.trunc_df

        return Runtime(self, c_name, pd.DataFrame(
            {
                'open': df[c_name+'_open'],
                'close': df[c_name+'_close'],
                'high': df[c_name+'_high'],
                'low': df[c_name+'_low'],
                'volume': df[c_name+'_volume']
            },
            index = df.index
        ))
