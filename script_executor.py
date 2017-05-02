''' Scripting executor
    Usage:
        python script_executor.py script:source#version [key=value ...]
'''

import sys
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'percms.settings'
django.setup()

import scripting.models

# Get args
script, args = sys.argv[1], sys.argv[2:]
