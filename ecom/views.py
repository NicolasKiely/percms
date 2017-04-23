from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from . import dashboard


@login_required
def view_dashboard(request):
    context = {
        'panels': [
            dashboard.Supplier_Dashboard.get_dashboard_panel()
        ]
    }
    return dashboard.App_Dashboard.render(request, context)

