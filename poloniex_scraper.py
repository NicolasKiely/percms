import django
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'percms.settings'
django.setup()

import crypto.poloniex_api
import crypto.models

if len(sys.argv) < 2:
    print 'Usage: python %s <api key name>' % sys.argv[0]
    api_keys = crypto.models.API_Key.objects.all()
    if len(api_keys):
        print 'Available Keys:'
    for key in api_keys:
        print '\t"%s"' % key.name
    sys.exit(0)

# Get api key
try:
    api_key = crypto.models.API_Key.objects.get(name=sys.argv[1])
except crypto.models.API_Key.DoesNotExist:
    print 'API key "%s" not found' % sys.argv[1]
    sys.exit(1)

polo = crypto.poloniex_api.poloniex(api_key.key, api_key.secret)

#print polo.returnTicker()['BTC_ETH']
print polo.returnMarketTradeHistory('BTC_ETH')[0]
