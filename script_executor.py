''' Scripting executor
    Usage:
        python script_executor.py script:source#version [key=value ...]
'''

import sys
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'percms.settings'
django.setup()

from scripting.models import Script, Source

argv = sys.argv
if len(argv)<2:
    print 'Usage: python %s <script:source#version> [arg=value ...]' % argv[0]
    sys.exit(1)

# Get args
script_arg, args = argv[1], argv[2:]


# Get script
script_cat, script_postfix = script_arg.split(':', 1)
script_postfix_split = script_postfix.split('#', 1)
script_name = script_postfix_split[0]

try:
    script = Script.objects.get(
        name=script_name, category=script_cat
    )
except Script.DoesNotExist:
    print 'Script not found: "%s:%s"' % (script_cat, script_name)
    sys.exit(1)

# Get script source
if len(script_postfix_split) == 1:
    # No version number
    source = Source.objects.order_by('-version').filter(script=script)[0]

else:
    # Use version
    script_version = script_postfix_split[1]
    source = Source.objects.get(script=script, version=script_version)

