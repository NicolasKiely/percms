""" Poloniex Exchange Interface """
from  exchange import Exchange
from crypto import poloniex_api


class Poloniex(Exchange.Interface):
    """ Poloniex """

    def get_connection(self):
        self.connection = poloniex_api.poloniex(
            self.key, self.secret
        )

    def get_balance(self):
        balances = Exchange.Balances()
        results = self.connection.returnBalances()

        for currency, value in results.iteritems():
            balances[currency] = value

        return balances
