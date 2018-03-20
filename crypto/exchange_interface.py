from bittrex.bittrex import Bittrex, API_V2_0
from . import models
from . import poloniex_api
from . import candle_sticks


def get_interface(exchange_name, *args, **kwargs):
    ''' Fetches interface by exchange name '''
    exc = exchange_name.lower()
    if exc == 'poloniex':
        return Poloniex_Interface(*args, **kwargs)
    elif exc == 'bittrex':
        return Bittrex_Interface(*args, **kwargs)


class Not_Implemented(Exception):
    def __init__(self, func):
        self.msg = 'Not Implemented: %s.%s' % (
            func.__class__.__name__, func.__name__
        )

    def __str__(self):
        return self.msg


class Exchange_Interface(object):
    ''' Abstract interface for handling exchanges '''
    def use_key(self, key):
        ''' Sets key '''
        if (type(key) is str) or (type(key) is unicode):
            self.api_key = models.API_Key.objects.get(name=key)
        elif type(key) is models.API_Key:
            self.api_key = key
        else:
            self.api_key = None

    def get_key_str(self):
        ''' Returns key # '''
        if self.api_key:
            return str(self.api_key.key)
        else:
            return ''

    def get_key_secret(self):
        ''' Returns key secret '''
        if self.api_key:
            return str(self.api_key.secret)
        else:
            return ''

    def get_balance(self):
        ''' Returns account balance '''
        raise Not_Implemented(self.get_balance)

    def update_candles(self):
        ''' Update candlestick data '''
        raise Not_Implemented(self.update_candles)



class Poloniex_Interface(Exchange_Interface):
    ''' Poloniex Interface '''
    def __init__(self, key):
        ''' Initializes and returns interface to poloniex '''
        self.use_key(key)
        self.connection = poloniex_api.poloniex(
            self.get_key_str(), self.get_key_secret()
        )

    def get_balance(self):
        return self.connection.returnBalances()

    def update_candles(self, logger):
        candle_sticks.update_poloniex(logger, self.connection)


class Bittrex_Interface(Exchange_Interface):
    ''' Bittrex Interface '''
    def __init__(self, key):
        self.use_key(key)
        self.connection = Bittrex(self.get_key_str(), self.get_key_secret())

    def get_balance(self):
        response = self.connection.get_balances()['result']
        balances = {}
        for record in response:
            balance = record['Balance']
            if balance > 0.0:
                balances[ record['Currency'] ] = balance
        return balances
        
