from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from .models import DocPage
from common import core

@login_required
def editor_list(request):
    ''' Top-level editor page for docs '''
    context = { }
    return core.render(request, 'docpage/editor_list.html', *context)


@login_required
def editor_page(request, pk):
    ''' Editor for a doc page '''
    context = { }
    return core.render(request, 'docpage/editor.html', *context)


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
