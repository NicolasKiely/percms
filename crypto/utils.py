from . import models

def get_currency_pair(exchange_name, currency1, currency2):
    ''' Fetches currency pair object by name '''
    exchange = models.Exchange.objects.get(name=exchange_name)
    return models.Pair.objects.get(exc=exchange, c1=currency1, c2=currency2)
