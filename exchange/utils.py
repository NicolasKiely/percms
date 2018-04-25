""" Utilities for exchange module """
import exchange.Poloniex


EXCHANGE_MAP = {
    'poloniex': exchange.Poloniex.Poloniex
}


def get_interface(interface_name, api_key):
    return EXCHANGE_MAP[interface_name.lower()](api_key)


def get_interface_class(interface_name):
    return EXCHANGE_MAP[interface_name.lower()]
