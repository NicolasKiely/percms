from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from . import models


@login_required
def view_dashboard(request):
    context = {
        'panels': [
            dashboard.Supplier_Dashboard.get_dashboard_panel()
        ]
    }
    return dashboard.App_Dashboard.render(request, context)


@login_required
def add_product(request, dashboard):
    ''' Add new product '''
    p = request.POST
    product = models.Product(
        name=p['name'],
        description=p['description'],
        inventory=p['inventory'],
        supplier=models.Supplier.objects.get(name=p['supplier'])
    )
    product.save()
    parent_dash = dashboard.get_parent('supplier')
    return HttpResponseRedirect(parent_dash.reverse_dashboard())
