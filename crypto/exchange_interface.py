""" DEPRECATED: use exchange.package """

import traceback
import datetime
from django.utils import timezone
from bittrex.bittrex import Bittrex, API_V2_0, TICKINTERVAL_HOUR
from . import models
from . import backtest
from . import poloniex_api
from . import candle_sticks
from . import runtime as crypto_runtime


def calculate_buy_amount(base_amount, ticker, total_amount, position_limit, buy_limit):
    buy_price = ticker * 1.001
    buy_limit_amt = total_amount * buy_limit / buy_price
    pos_limit_amt = (base_amount - total_amount*(1-position_limit)) / buy_price
    buy_amt = min(base_amount / buy_price, buy_limit_amt, pos_limit_amt)
    return max(buy_amt, 0.0), buy_price


def get_interface(exchange_name, *args, **kwargs):
    """ Fetches interface by exchange name """
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
    """ Abstract interface for handling exchanges """
    def use_key(self, key):
        """ Sets key """
        if (type(key) is str) or (type(key) is unicode):
            self.api_key = models.API_Key.objects.get(name=key)
        elif type(key) is models.API_Key:
            self.api_key = key
        else:
            self.api_key = None

    def get_key_str(self):
        """ Returns key # """
        if self.api_key:
            return str(self.api_key.key)
        else:
            return ''

    def get_key_secret(self):
        """ Returns key secret """
        if self.api_key:
            return str(self.api_key.secret)
        else:
            return ''

    def get_balance(self):
        """ Returns account balance """
        raise Not_Implemented(self.get_balance)

    def update_candles(self, logger):
        """ Update candlestick data """
        raise Not_Implemented(self.update_candles)

    def get_ticker_prices(self, base_name, pair_names):
        """ Returns ticker prices """
        raise Not_Implemented(self.get_ticker_prices)

    def eval_portfolio(self, logger, portfolio, commit):
        """ Evaluates a portfolio """
        # Initialize pair name variables
        portfolio_pairs = portfolio.pairs.all()
        c_names = [p.c2 for p in portfolio_pairs]
        c_name_set = set(c_names)
        pair_lookup = {p.c2: p for p in portfolio_pairs}

        # Initialize balances
        balances = {c: 0.0 for c in c_names}
        fetched_balances = self.get_balance()

        # Set up base variables
        base_name = portfolio.base_currency.symbol
        base_amount = 0.0 # Amount of base Currency
        total_amount = 0.0 # Total tracked portfolio amount

        # Get latest ticker prices
        ticker_prices = self.get_ticker_prices(base_name, c_names)

        # fetch and calculate balances
        fetched_balances = self.get_balance()
        for c, v in fetched_balances.iteritems():
            fv = float(v)
            if c == base_name:
                base_amount = fv
                total_amount += base_amount

            elif fv > 0:
                if c in c_name_set:
                    balances[c] = fv
                    total_amount += fv * ticker_prices[base_name + '_' + c]

        # Initialize runtime
        runtime_factory = crypto_runtime.Runtime_Factory(portfolio.pairs.all())
        dt_stop = timezone.now()
        dt_start = dt_stop - datetime.timedelta(days=365)
        runtime_factory.load_data(dt_start, dt_stop, period=portfolio.period)
        positions = {c: '....' for c in c_names}
        stoplosses = {}

        # Save current balance history
        history_record = models.Portfolio_History(
            stamp=timezone.now(), portfolio=portfolio,
            base_holding=base_amount, total_holding=total_amount
        )
        history_record.save()
        for c in c_names:
            amt = balances[c]
            last_price = ticker_prices[base_name + '_' + c]
            position_record = models.Portfolio_Position_History(
                history=history_record, pair=pair_lookup[c],
                amount_held=amt, value_held=amt*last_price
            )
            position_record.save()

        # Calculate positions
        for c_name in c_names:
            # Iterate over currencies
            try:
                global runtime
                runtime = runtime_factory.runtime(c_name)

                # Load stoploss if applicable
                if balances[c_name]:
                    pos_record, created = models.Portfolio_Position.objects.get_or_create(
                        portfolio=portfolio, pair=pair_lookup[c_name]
                    )
                    if pos_record.stoploss:
                        runtime.set_stoploss(pos_record.stoploss)

                exec(portfolio.script.source)

            except Exception as ex:
                trace = traceback.format_exc()
                print(trace)
                raise backtest.Backtest_Exception('Script Exception: %s' % trace)

            candle = runtime.data.iloc[-1]
            last_price = ticker_prices[base_name + '_' + c_name]

            if runtime.is_stoploss_enabled():
                stoplosses[c_name] = runtime.get_stoploss()

            if runtime.is_stoploss_enabled() and last_price<runtime.get_stoploss():
                # Stoploss
                positions[c_name] = 'STOP'

            elif runtime.signal == 'LONG':
                positions[c_name] = 'LONG'

            elif runtime.signal == 'SELL':
                positions[c_name] = 'SELL'

            else:
                positions[c_name] = '....'

        # Act on position: sells first, then buys
        for c_name in c_names:
            # Log position
            p = positions[c_name]
            bal = balances[c_name]

            pos_record, created = models.Portfolio_Position.objects.get_or_create(
                portfolio=portfolio, pair=pair_lookup[c_name]
            )
            pos_record.position = p
            if (c_name in stoplosses) and (p == 'LONG' or bal > 0):
                pos_record.stoploss = stoplosses[c_name]
            else:
                pos_record.stoploss = None
            pos_record.save()

            # Handle sells
            if not (p == 'STOP' or p == 'SELL'):
                continue

            if bal > 0:
                pair_name = base_name + '_' + c_name
                print('Sell ' + c_name + ' for ' + str(bal))
                # cancel_old_orders(polo, pair_name)
                sell_price = 0.999*ticker_prices[pair_name]

                if commit:
                    # q = polo.sell(str(pair_name), str(sell_price), str(bal))
                    q = {'orderNumber': 'test'}
                else:
                    q = {'orderNumber': 'test'}
                logger.log('Sell Order Placed', '\n'.join([
                    'Order #: ' + str(q['orderNumber']),
                    'Sell Price: ' + str(sell_price),
                    'Sell Amount: ' + str(bal),
                    '',
                    'Current ' + base_name + ' Amt: ' + str(base_amount),
                    'Total Portfolio Value: ' + str(total_amount),
                    'Base to release: ' + str(sell_price*bal)
                ]))

        for c_name in c_names:
            # Handle buys
            p = positions[c_name]
            if p != 'LONG':
                continue

            pair_name = base_name + '_' + c_name
            buy_amt, buy_price = calculate_buy_amount(
                base_amount, ticker_prices[pair_name], total_amount,
                portfolio.position_limit, portfolio.buy_limit
            )
            if base_amount > 0 and buy_amt > 0.0:
                print('Buy %s of %s @ %s' % (buy_amt, c_name, buy_price))

                # cancel_old_orders(polo, pair_name)
                    
                if commit:
                    # q = polo.buy(str(pair_name), str(buy_price), str(buy_amt))
                    q = {'orderNumber': 'test'}
                else:
                    q = {'orderNumber': 'test'}

                logger.log('Buy Order Placed', '\n'.join([
                    'Order #: ' + str(q['orderNumber']),
                    'Buy Price: ' + str(buy_price),
                    'Buy Amount: ' + str(buy_amt),
                    '',
                    'Current ' + base_name + ' Amt: ' + str(base_amount),
                    'Total Portfolio Value: ' + str(total_amount),
                    'Base to commit: ' + str(buy_price*buy_amt)
                ]))
                break


class Poloniex_Interface(Exchange_Interface):
    """ Poloniex Interface """
    def __init__(self, key):
        """ Initializes and returns interface to poloniex """
        self.use_key(key)
        self.connection = poloniex_api.poloniex(
            self.get_key_str(), self.get_key_secret()
        )

    def get_balance(self):
        return self.connection.returnBalances()

    def update_candles(self, logger):
        candle_sticks.update_poloniex(logger, self.connection)


class Bittrex_Interface(Exchange_Interface):
    """ Bittrex Interface """
    def __init__(self, key):
        self.use_key(key)
        self.connection = Bittrex(
            self.get_key_str(), self.get_key_secret(), api_version=API_V2_0
        )

    def get_balance(self):
        response = self.connection.get_balances()['result']
        balances = {}
        for record in response:
            balance = record['Balance']['Balance']
            currency = record['Currency']['Currency']
            if balance > 0.0:
                balances[currency] = balance
        return balances
        
    def update_candles(self, logger):
        candle_sticks.update_bittrex(logger, self.connection)

    def get_ticker_prices(self, base_name, pair_names):
        ticker_prices = {}
        for pair_name in pair_names:
            latest_candle = self.connection.get_latest_candle(
                base_name + '-' + pair_name, TICKINTERVAL_HOUR
            )['result'][0]
            ticker_prices[pair_name] = float(latest_candle['C'])
        return ticker_prices
