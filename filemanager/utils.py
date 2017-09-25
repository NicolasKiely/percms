from django.utils import timezone
from .models import Meta_File
from percms import safesettings


def create_file_record(category, file_name, is_image):
    ''' Create metafile record '''
    now = timezone.now()

    meta_file = Meta_File(
        name=file_name,
        category=category,
        dt_uploaded=now,
        is_img=is_image
    )
    meta_file.save()
    return meta_file


def save_file(data, category, file_name, is_image=False):
    ''' Saves file to store, then return file record handle '''
    now = timezone.now()

    # Create record and save contents
    meta_file = create_file_record(category, file_name, is_image)
    save_path = meta_file.get_file_path()

    with open(save_path, 'wb+') as dest:
        dest.write(data)

    return meta_file
