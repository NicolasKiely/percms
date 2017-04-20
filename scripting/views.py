from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from common import core
from .dashboard import Dashboard, Script_Dashboard


@login_required
def dashboard(request):
    context = {
        'panels': [
            Script_Dashboard.get_dashboard_panel()
        ]
    }
    #return core.render(request, 'common/app_dashboard.html', **context)
    return Dashboard.render(request, context)
