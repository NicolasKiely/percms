from . import models
from . import poloniex_api


class Exchange_Interface(object):
    ''' Abstract interface for handling exchanges '''


class Poloniex_Interface(Exchange_Interface):
    ''' Poloniex Interface '''
    def __init__(self, keyname='Poloniex'):
        ''' Initializes and returns interface to poloniex '''
        self.api_key = models.API_Key.objects.get(name=keyname)
        self.connection = poloniex_api.poloniex(
            self.api_key.key, self.api_key.secret
        )

    
    def update_candles(self):
        ''' Update candlestick data '''
        pass


    def get_balance(self):
        ''' Returns account balance '''
        pass


class Bittrex_Interface(Exchange_Interface):
    ''' Bittrex Interface '''
