import django
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'percms.settings'
django.setup()

print 'done'
