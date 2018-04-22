""" Utilities for exchange module """
import exchange.Poloniex


def get_interface(inteface_name, api_key):
    lname = inteface_name.lower()
    if lname == 'poloniex':
        return exchange.Poloniex.Poloniex(api_key)
