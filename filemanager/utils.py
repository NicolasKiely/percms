from django.utils import timezone
from .models import Meta_File
from percms import safesettings

def get_meta_file_path(meta_file):
    ''' Gets filename for given meta file '''
    sid = str(meta_file.id)

    if meta_file.is_img:
        save_path = safesettings.UPLOAD_IMAGE_PATH + sid
    else:
        save_path = safesettings.UPLOAD_FILE_PATH + sid
    return save_path


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
    save_path = get_meta_file_path(meta_file)

    with open(save_path, 'wb+') as dest:
        dest.write(data)

    return meta_file
