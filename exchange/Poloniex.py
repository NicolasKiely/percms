""" Poloniex Exchange Interface """
from  exchange import Exchange
from crypto import poloniex_api


class Poloniex(Exchange.Interface):
    """ Poloniex.

     Uses uppercase short designations for currency names, and
     underscores for pairs.
     """
    @staticmethod
    def parse_pair(pair):
        """ Returns tuple pair of currency string.

        eg 'BTC_ETH' -> (BTC, ETH)
        """
        return pair.split('_')

    def get_connection(self):
        self.connection = poloniex_api.poloniex(
            self.key, self.secret
        )

    def get_balance(self):
        balances = Exchange.Currency_Values()
        results = self.connection.returnBalances()

        for currency, value in results.items():
            balances[currency] = value

        return balances

    def get_ticker(self):
        # Returned by ticker: last, quoteVolume, high24hr, isFrozen,
        # highestBid, percentChange, low24hr, lowestAsk, id, baseVolume
        ticker = Exchange.Pair_Values(self.parse_pair)
        results = self.connection.returnTicker()

        for currency, value in results.items():
            ticker[currency] = value['last']

        return ticker
