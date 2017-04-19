from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from common import core


@login_required
def dashboard(request):
    context = {
        'title': 'Script Dashboard',
        'app': {
            'name': 'Script'
        },

        'panels': [
            {
                'title': 'Scripts',
                'table': {
                    'headers': ['Script Name', 'URL'],
                    'rows': [
                    ]
                }
            }
        ]
    }
    return core.render(request, 'common/app_dashboard.html', **context)
