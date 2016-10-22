from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import DocPage, Panel, Component, mchoices, vchoices
from .dynamic_views import view_table
import component_utils
from common import core
import json
import re

# Pattern for matching dashes and underscores
dash_pattern = re.compile('[-_]+')


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
        # Get panel data
        panel_json = {'header': panel.title, 'components': []}
        for comp in panel.component_set.all():
            # Get component data
            comp_json = {
                'source': comp.src, 'model': comp.model, 'view': comp.view
            }
            panel_json['components'].append(comp_json)

        panels_json.append(panel_json)

    context = {
        'docpage': docPage,
        'panels': json.dumps(panels_json),
        'mchoices': json.dumps(mchoices),
        'vchoices': json.dumps(vchoices),
        'page': {
            'user_menu': [
                (reverse('docpage:view_page', args=(docPage.id,)), 'View This Page')
            ],
            'title': docPage.title.title() +' - PerCMS'
        }
    }
    return core.render(request, 'docpage/editor.html', **context)


@login_required
def edit_page(request):
    ''' Edit doc page action '''
    pk = request.POST['pk']
    docPage = get_object_or_404(DocPage, pk=pk)
    docPage.category = request.POST['category']
    docPage.title = request.POST['title']
    panel_specs = json.loads(request.POST['panel_data'])

    # Drop old panel and component data
    docPage.panel_set.all().delete()

    # Save new panel/component data
    for panel_spec in panel_specs:
        # Iterate over panel post objects
        new_panel = Panel(title=panel_spec['header'], page=docPage)
        new_panel.save()

        for comp_spec in panel_spec['components']:
            # Iterate over component objects
            new_comp = Component(panel=new_panel, src=comp_spec['source'],
                model=comp_spec['model'], view=comp_spec['view']
            )
            new_comp.save()

    docPage.dt_editted = timezone.now()
    docPage.save()
    return HttpResponseRedirect(
        reverse('docpage:editor_page', args=(pk,))
    )


def view_page(request, pk):
    ''' Displays public page '''
    docpage = get_object_or_404(DocPage, pk=pk)
    return render_page(request, docpage)


def view_by_name(request, category, title):
    ''' Display page retrieved by name '''
    docpage = get_object_or_404(DocPage, title=title, category=category)
    return render_page(request, docpage)


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


def render_page(request, docpage):
    ''' Renders a specific docpage '''
    # Pre-process components
    panels = []
    panel_specs = docpage.panel_set.all()[:]
    for panel_spec in panel_specs:
        # For each panel
        panel = {'title': panel_spec.title, 'components': []}
        for comp_spec in panel_spec.component_set.all():
            # For each component
            comp = {'view': comp_spec.view,
                'model': comp_spec.model, 'src': comp_spec.src}

            if comp['view'] == 'table':
                # Structure table
                comp['safe'] = (comp['model'] != 'raw')

                if comp['model'] in ('raw', 'html'):
                    comp['table'] = component_utils.preprocess_raw_table(comp['src'])

            elif comp['view'] == 'text':
                # Text post
                if comp['model'] == 'raw':
                    # Break up lines into paragraphs
                    comp['paragraphs'] = component_utils.preprocess_text(comp['src'])

            # Handle dynamic views
            if comp['model'] == 'dapi':
                try:
                    dapi_module, dapi_func = comp['src'].split(':')
                    func = view_table[dapi_func]
                    func(comp)
                except KeyError:
                    comp['view'] = 'text'
                    comp['model'] = 'raw'
                    err_msg = 'Error: Could not lookup dapi call '+comp['src']
                    comp['paragraphs'] = [err_msg]

            panel['components'].append(comp)
        panels.append(panel)
        
    page_title = dash_pattern.sub(' ', docpage.title).title()

    context = {
        'docpage': docpage, 'panels': panels,
        'page': {
            'user_menu': [
                (reverse('docpage:editor_page', args=(docpage.id,)), 'Edit This Page')
            ],
            'title': page_title +' - PerCMS'
        }
    }

    # Add page description if text
    if len(panel_specs) > 0:
        panel_spec = panel_specs[0]
        comp_specs = list(panel_spec.component_set.all()[:1])
        if comp_specs:
            comp_spec = comp_specs[0]
            if comp_spec.view=='text' and comp_spec.model=='raw':
                context['page']['description'] = comp_spec.src.split('.', 1)[0]
            
    return core.render(request, 'docpage/docpage.html', **context)
