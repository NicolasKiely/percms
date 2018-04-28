from . import models


def get_currency_pair(exchange_id, currency1, currency2):
    """ Fetches currency pair object by name, id, or model """
    t_exchange = type(exchange_id)
    if t_exchange is int:
        exchange = models.Exchange.objects.get(id=exchange_id)
    elif t_exchange is models.Exchange:
        exchange = exchange_id
    else:
        exchange = models.Exchange.objects.get(name=exchange_id)
    return models.Pair.objects.get_or_create(
        exc=exchange, c1=currency1, c2=currency2
    )[0]
