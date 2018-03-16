import urllib2
import traceback
import datetime
from django.utils import timezone
from . import poloniex_api
from . import backtest
from . import runtime as crypto_runtime
from . import models


def calculate_buy_amount(base_amount, ticker, total_amount, position_limit, buy_limit):
    buy_price = ticker * 1.001
    buy_limit_amt = total_amount * buy_limit / buy_price
    pos_limit_amt = (base_amount - total_amount*position_limit) / buy_price
    buy_amt = min(base_amount / buy_price, buy_limit_amt, pos_limit_amt)
    return max(buy_amt, 0.0), buy_price


def eval_poloniex_portfolio(logger, portfolio, commit=True):
    ''' Evaluates portfolio on poloniex exchange '''
    api_key = portfolio.key
    polo = poloniex_api.poloniex(str(api_key.key), str(api_key.secret))
    try:
        polo_balances = polo.returnBalances()
    except urllib2.HTTPError as ex:
        logger.write('Error, do not have permission to access account balance')
        raise backtest.Backtest_Exception(str(ex))

    portfolio_pairs = portfolio.pairs.all()
    c_names = [p.c2 for p in portfolio_pairs]
    c_name_set = set(c_names)
    pair_lookup = {p.c2: p for p in portfolio_pairs}
    balances = {c: 0.0 for c in c_names}

    base_name = portfolio.base_currency.symbol
    base_amount = 0.0 # Amount of base Currency
    total_amount = 0.0 # Total tracked portfolio amount

    # Get latest ticker prices
    ticker = polo.returnTicker()
    ticker_prices = {}
    for k, v in ticker.iteritems():
        ticker_prices[k] = float(v['last'])

    # Calculate balances
    for c, v in polo_balances.iteritems():
        fv = float(v)
        if c == base_name:
            base_amount = fv
            total_amount += base_amount

        elif fv > 0:
            if c in c_name_set:
                balances[c] = fv
                total_amount += fv * ticker_prices[base_name+'_'+c]
            #balances[c] = fv
            #if not c in c_name_set:
            #    c_names.append(c)
            #    c_name_set.add(c)

    print "Base amount: ", base_name, base_amount
    for c in c_names:
        print c, balances[c]

    # Initialize runtime
    runtime_factory = crypto_runtime.Runtime_Factory(portfolio.pairs.all())
    dt_stop = timezone.now()
    dt_start = dt_stop - datetime.timedelta(days=365)
    runtime_factory.load_data(dt_start, dt_stop, period=portfolio.period)
    positions = {c: '....' for c in c_names}
    stoplosses = {}

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
            print trace
            raise backtest.Backtest_Exception('Script Exception: %s' % trace)

        candle = runtime.data.iloc[-1]
        last_price = ticker_prices[base_name+'_'+c_name]

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
        if (c_name in stoplosses) and (p=='LONG' or bal>0):
            pos_record.stoploss = stoplosses[c_name]
        else:
            pos_record.stoploss = None
        pos_record.save()

        # Handle sells
        if not (p == 'STOP' or p == 'SELL'):
            continue
        #if bal > 0:
        print 'Sell '+ c_name +' for '+ str(bal)
    
    for c_name in c_names:
        # Handle buys
        p = positions[c_name]
        if p != 'LONG':
            continue

        pair_name = base_name +'_'+ c_name
        buy_amt, buy_price = calculate_buy_amount(
            base_amount, ticker_prices[pair_name], total_amount,
            portfolio.position_limit, portfolio.buy_limit
        )
        if base_amount > 0 and buy_amt > 0.0:

            print 'Buy %s of %s @ %s' % (buy_amt, c_name, buy_price)
            orders = polo.returnOpenOrders(pair_name)

            for order in orders:
                order_no = order['orderNumber']
                print 'Cancelling order #%s' % (order_no)
                print polo.cancel(pair_name, order_no)
                
            if commit:
                q = polo.buy(str(pair_name), str(buy_price), str(buy_amt))
            else:
                q = {'orderNumber': 'test'}

            logger.log('Buy Order Placed', '\n'.join([
                'Order #: '+ str(q['orderNumber']),
                'Buy Price: '+ str(buy_price),
                'Buy Amount: '+ str(buy_amt),
                '',
                'Current '+ base_name +' Amt: '+ str(base_amount),
                'Total Portfolio Value: '+ str(total_amount),
                'Base to commit: '+ str(buy_price*buy_amt)
            ]))
            break
