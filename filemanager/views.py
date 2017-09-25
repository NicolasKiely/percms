from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from PIL import Image
from common import core
from percms import safesettings
from .models import Meta_File
from .utils import save_file


def upload(request):
    ''' Upload file page '''
    context = {}
    if request.method == 'POST' and request.FILES:
        # Handle saving file
        fh = request.FILES.values()[0] # file
        if fh.size > 4*1024*1024:
            context['too_big'] = True
        else:
            now = timezone.now()

            # Check if file is image
            try:
                attempt_image = Image.open(fh)
                is_image = True
            except IOError:
                is_image = False

            # Create and save file
            meta_file = save_file(
                data = fh.read(),
                category=request.POST['category'],
                file_name=request.POST['name'],
                is_image=is_image
            )
            

            # Pass file information back to page
            context['file'] = meta_file
            context['file_url'] = 'images/'+ str(meta_file.id)

    return core.render(request, 'filemanager/upload.html', **context)


def describe(request, pk):
    ''' Shows image meta data '''
    meta_file = get_object_or_404(Meta_File, pk=pk)
    context = {'file': meta_file, 'file_url': 'images/'+str(meta_file.id)}

    return core.render(request, 'filemanager/describe.html', **context)


def download(request, pk):
    ''' Download link for data '''
    meta_file = get_object_or_404(Meta_File, pk=pk)
    file_path = meta_file.get_file_path()
    with open(file_path, 'r') as fh:
        response = HttpResponse(fh.read())
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename="%s"' % meta_file.name
        return response

def view_by_name(request, resource):
    ''' Loads file by name '''
    try:
        meta_file = Meta_File.objects.filter(name=resource).latest('dt_uploaded')
    except ObjectDoesNotExist:
        raise Http404("File Not Found")

    if meta_file.is_img:
        save_path = safesettings.UPLOAD_IMAGE_PATH + str(meta_file.id)
    else:
        save_path = safesettings.UPLOAD_FILE_PATH + str(meta_file.id)

    with open(save_path, 'r') as fh:
        return HttpResponse(fh.read())
