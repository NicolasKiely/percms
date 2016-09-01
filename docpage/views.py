from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import DocPage
from common import core

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
    context = {
        'docpage': docPage
    }
    return core.render(request, 'docpage/editor.html', **context)


@login_required
def edit_header(request):
    ''' Edits doc page's header '''
    pk = request.POST['pk']
    docPage = get_object_or_404(DocPage, pk=pk)
    docPage.category = request.POST['category']
    docPage.title = request.POST['title']
    docPage.dt_editted = timezone.now()
    docPage.save()
    return HttpResponseRedirect(
        reverse('docpage:editor_page', args=(pk,))
    )
    


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
