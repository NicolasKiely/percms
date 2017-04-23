from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from . import models
from crawler.models import Website


@login_required
def view_dashboard(request):
    context = {
        'panels': [
            dashboard.Supplier_Dashboard.get_dashboard_panel()
        ]
    }
    return dashboard.App_Dashboard.render(request, context)

@login_required
def edit_supplier(request, dashboard):
    ''' Edit a supplier's info '''
    p = request.POST
    supplier = get_object_or_404(models.Supplier, pk=p['pk'])
    supplier.name = p['name']
    supplier.description = p['description']
    
    domain = p['website']
    try:
        website = Website.objects.get(domain=domain)
    except Website.DoesNotExist:
        website = Website(domain=domain)
        website.save()
    supplier.website = website
    
    supplier.save()
    return HttpResponseRedirect(dashboard.reverse_dashboard())


@login_required
def add_product(request, dashboard):
    ''' Add new product '''
    p = request.POST
    supplier = models.Supplier.objects.get(name=p['supplier']) 
    product = models.Product(
        name=p['name'],
        description=p['description'],
        inventory=p['inventory'],
        supplier=supplier
    )
    product.save()
    parent_dash = dashboard.get_parent('supplier')
    return HttpResponseRedirect(parent_dash.reverse_editor(supplier.id))
