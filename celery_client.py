import os
import sys
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'percms.settings'
django.setup()

import crypto.tasks

commands = {
    'poloniex_candles_update': crypto.tasks.poloniex_candles_update
}


if len(sys.argv) == 1:
    print 'Usage: python %s <command> [parameter=value] ...' % sys.argv[0]
    print 'Try python %s batch/help to see list of functions' % sys.argv[0]
    print '\tor pythor %s batch/reload to reload functions' % sys.argv[0]
    sys.exit(0)

command = sys.argv[1]
post_arg_list = [x.split('=') for x in sys.argv[2:]]
post_args = {k: v for k, v in post_arg_list}

commands[command].delay(**post_args)
