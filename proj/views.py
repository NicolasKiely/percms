from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from common import core
from .models import Proj
from docpage.models import DocPage
from docpage.views import build_docpage_context


@login_required
def editor_list(request):
    ''' Top-levbel editor page for projects '''
    context = {
        'projects': Proj.objects.order_by('-dt_published')
    }
    return core.render(request, 'proj/editor_list.html', **context)


@login_required
def editor(request, pk):
    ''' Editor for a project '''
    project = get_object_or_404(Proj, pk=pk)
    context = { 'project': project }
    if project.about_page:
        context['about_page'] = project.about_page.id
    return core.render(request, 'proj/editor.html', **context)


@login_required
def edit(request):
    ''' Post handle for editting a project '''
    pk = request.POST['pk']
    # Set project text fields
    project = get_object_or_404(Proj, pk=pk)
    project.category = request.POST['category']
    project.title = request.POST['title']
    project.repo_URL = request.POST['repo']

    # Set project about page id
    about = request.POST['about']
    if about != '':
        project.about_page = DocPage.objects.get(pk=int(about))
    else:
        project.about_page = None

    project.save()
    return HttpResponseRedirect(
        reverse('project:editor', args=(pk,))
    )


@login_required
def add(request):
    ''' Post handle for adding a new project '''
    projCat = request.POST['category']
    projTitle = request.POST['title']
    now = timezone.now()

    # Create new project
    project = Proj(
        title=projTitle, category=projCat, dt_published=now
    )
    project.save()

    return HttpResponseRedirect(
        reverse('project:editor', args=(project.id,))
    )


def view(request, pk):
    ''' Displays project '''
    project = get_object_or_404(Proj, pk=pk)
    docpage = project.about_page
    context = build_docpage_context(docpage)
    context['project'] = project
    
    context['page']['user_menu'] = [
        (reverse('docpage:editor_page', args=(docpage.id,)), 'Edit Description'),
        (reverse('project:editor', args=(project.id,)), 'Edit Project')
    ]

    page_title = project.title.title()
    context['page']['title'] = page_title + ' - PerCMS'
    return core.render(request, 'proj/view.html', **context)
