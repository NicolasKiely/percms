from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from . import dashboard

# Create your views here.

@login_required
def view_dashboard(request):
    context = {
        'panels': [
            dashboard.Supplier_Dashboard.get_dashboard_panel()
        ]
    }
    return dashboard.App_Dashboard.render(request, context)
