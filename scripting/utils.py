''' Utilities for scripting '''
from .models import Script, Source


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
