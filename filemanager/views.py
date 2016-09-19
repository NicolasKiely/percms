from django.utils import timezone
from PIL import Image
from common import core
from percms import safesettings
from .models import Meta_File


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
            meta_file = Meta_File(
                name=request.POST['name'],
                category=request.POST['category'],
                dt_uploaded=now,
                is_img=is_image
            )
            meta_file.save()
            
            # Save file contents
            sid = str(meta_file.id)
            if meta_file.is_img:
                save_path = safesettings.UPLOAD_IMAGE_PATH + sid
            else:
                save_path = safesettings.UPLOAD_FILE_PATH + sid

            with open(save_path, 'wb+') as dest:
                for chunk in fh.chunks():
                    dest.write(chunk)

            # Pass file information back to page
            context['file'] = meta_file
            context['file_url'] = 'images/'+ sid

    return core.render(request, 'filemanager/upload.html', **context)
