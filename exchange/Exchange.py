from abc import abstractmethod
import crypto.models


class Interface(object):
    """ Exchange Interface """
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


class Balances(object):
    """ Instance of asset balances for an account """
    def __init__(self):
        self.balances = {}

    def __setitem__(self, asset, balance):
        self.balances[asset.upper()] = float(balance)

    def __getitem__(self, asset):
        uasset = asset.upper()
        if uasset in self.balances:
            return self.balances[uasset]
        else:
            return 0.0

    def __str__(self):
        return '\n'.join(['%s: %s' % (k, v) for k, v in self.balances.items()])

    def __iter__(self):
        return self.balances.items()
