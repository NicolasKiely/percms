from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import DocPage, Panel
from common import core
import json


@login_required
def editor_list(request):
    ''' Top-level editor page for docs '''
    context = {
        'docpages': DocPage.objects.order_by('-dt_editted')
    }

    return core.render(request, 'docpage/editor_list.html', **context)


@login_required
def editor_page(request, pk):
    ''' Editor for a doc page '''
    docPage = get_object_or_404(DocPage, pk=pk)
    panels_json = []

    for panel in docPage.panel_set.all():
        panel_json = {'header': panel.title}
        panels_json.append(panel_json)

    context = { 'docpage': docPage, 'panels': json.dumps(panels_json) }
    return core.render(request, 'docpage/editor.html', **context)


@login_required
def edit_page(request):
    ''' Edit doc page action '''
    pk = request.POST['pk']
    docPage = get_object_or_404(DocPage, pk=pk)
    docPage.category = request.POST['category']
    docPage.title = request.POST['title']
    panel_specs = json.loads(request.POST['panel_data'])

    # TODO: Drop old panel and component data

    # TODO: Add new panel and component data
    for panel_spec in panel_specs:
        # Iterate over panel post objects
        new_panel = Panel(title=panel_spec['header'], page=docPage)
        new_panel.save()

    docPage.dt_editted = timezone.now()
    docPage.save()
    return HttpResponseRedirect(
        reverse('docpage:editor_page', args=(pk,))
    )


def view_page(request, pk):
    ''' Displays public page '''
    docPage = get_object_or_404(DocPage, pk=pk)
    context = { 'docpage': docPage }
    return core.render(request, 'docpage/docpage.html', **context)


@login_required
def add_page(request):
    ''' Post handle for adding a new page '''
    dpCategory = request.POST['category']
    dpTitle = request.POST['title']
    now = timezone.now()

    # Create new document page
    docPage = DocPage(
        title=dpTitle, category=dpCategory, dt_published=now, dt_editted=now
    )
    docPage.save()

    return HttpResponseRedirect(
        reverse('docpage:editor_page', args=(docPage.id,))
    )
