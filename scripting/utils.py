''' Utilities for scripting '''
from .models import Script, Source, Log_Message
from django.utils import timezone


def get_script_by_name(script_str):
    ''' Return (script,source) by string name: <category>:<name>[#version] '''
    # Get script
    script_cat, script_postfix = script_str.split(':', 1)
    script_postfix_split = script_postfix.split('#', 1)
    script_name = script_postfix_split[0]

    script = Script.objects.get(name=script_name, category=script_cat)

    # Get script source
    if len(script_postfix_split) == 1:
        # No version number
        source = Source.objects.order_by('-version').filter(script=script)[0]

    else:
        # Use version
        script_version = script_postfix_split[1]
        source = Source.objects.get(script=script, version=script_version)

    return script, source


class Logger_Callback(object):
    ''' Callback for runtime '''
    def callback(self, msg):
        print msg

class Logging_Runtime(object):
    ''' Scripting runtime logging tool '''
    def __init__(self, app_name, callback=None):
        ''' Initialize logger to use app name '''
        self.app_name = app_name
        self.callback = callback if callback else Logger_Callback()
        self.messages = []


    def write(self, msg):
        self.callback.callback(msg)
        

    def log(self, short_message='', long_message=''):
        ''' Log message to scripting database '''
        msg = Log_Message(
            stamp = timezone.now(),
            app_name = self.app_name,
            short_message = short_message,
            long_message = long_message
        )
        msg.save()
        self.messages.append(msg)
