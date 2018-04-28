from abc import abstractmethod
import time
import crypto.models


class Interface(object):
    """ Exchange Interface """
    #: Maximum requests per second (soft limit). Set <1 to disable
    _max_request_rate = 5

    def __init__(self, api_key):
        """ Initializes with given api key """
        if (type(api_key) is str) or (type(api_key) is unicode):
            self.api_key = crypto.models.API_Key.objects.get(name=api_key)
        elif type(api_key) is crypto.models.API_Key:
            self.api_key = api_key
        else:
            self.api_key = None

        self.connection = None
        if self.api_key:
            # Initialize instance connection
            self.get_connection()

    @property
    def key(self):
        """ Exchange api connection key """
        if self.api_key:
            return str(self.api_key.key)
        else:
            return ''

    @property
    def secret(self):
        """ Exchange api connection secret """
        if self.api_key:
            return str(self.api_key.secret)
        else:
            return ''

    @abstractmethod
    def get_connection(self):
        """ Initializes connection """
        pass

    @abstractmethod
    def get_balance(self):
        """ Fetches balance from exchange"""
        pass

    @abstractmethod
    def get_ticker(self):
        """ Fetches ticker price from exchange """
        pass

    def sleep(self, old_time=0.0):
        """ Sleeps between request to stay below limit """
        if self._max_request_rate <= 0:
            # No rate set
            return

        current_time = time.time()
        if old_time:
            # Track elapsed time
            delta = current_time - old_time

            if delta < 0:
                # Catch any weird cases causing old time to be in the future
                delta = 0

            # Get the wait period
            default_wait_period = 1. / self._max_request_rate

            # Deduct existing delta from default wait period
            sleep_period = default_wait_period - delta
            if sleep_period > 0:
                self.sleep(sleep_period)


class Currency_Values(object):
    def __init__(self):
        """ Holder of currency values """
        #: Mapping of assets to floating values
        self._assets = {}

    def __setitem__(self, asset, value):
        self._assets[asset.upper()] = float(value)

    def __getitem__(self, asset):
        uasset = asset.upper()
        if uasset in self._assets:
            return self._assets[uasset]
        else:
            return 0.0

    def items(self):
        return self._assets.items()

    def __str__(self):
        return '\n'.join([
            '%s: %s' % (asset, value)
            for asset, value in self._assets.items()
            if value
        ])


class Pair_Values(object):
    def __init__(self, parser):
        """ Holder of asset pair values """
        #: Mapping of pair to float values
        self._assets = {}
        #: Parser of input string into pair
        self._parser = parser

    def parser(self, obj):
        """ Conditionally parse if string """
        t_obj = type(obj)
        if t_obj is str or t_obj is unicode:
            results = self._parser(obj.upper())
            return results[0], results[1]
        else:
            return obj

    def __setitem__(self, assets, value):
        self._assets[self.parser(assets)] = float(value)

    def __getitem__(self, assets):
        results = self.parser(assets)
        if results in self._assets:
            return self._assets[results]
        else:
            return 0.0

    def items(self):
        return self._assets.items()

    def __str__(self):
        return '\n'.join([
            '%s: %s' % (asset, value)
            for asset, value in self._assets.items()
            if value
        ])
