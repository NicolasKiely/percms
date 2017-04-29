'''
Django settings and default configs that are safe to commit to a repository

To override a setting here, just create and set a variabe with the same name
in settings.py
'''
from percms import settings


# Flag for using local scripts, instead of CDNs
try:
    USE_LOCAL_ASSETS = settings.USE_LOCAL_ASSETS
except AttributeError:
    USE_LOCAL_ASSETS = False


# Site title
try:
    SITE_TITLE = settings.SITE_TITLE
except AttributeError:
    SITE_TITLE = 'PerCMS Website'


# Path for images. In production, it's advisable to set this to static
# path accessible by webserver.
try:
    UPLOAD_IMAGE_PATH = settings.UPLOAD_IMAGE_PATH
except AttributeError:
    UPLOAD_IMAGE_PATH = 'filemanager/static/images/'


# Path for storing arbitrary files.
try:
    UPLOAD_FILE_PATH = settings.UPLOAD_FILE_PATH
except AttributeError:
    UPLOAD_FILE_PATH = 'filemanager/static/files/'

# Path for storing crawler data
try:
    UPLOAD_CRAWLER_PATH = settings.UPLOAD_CRAWLER_PATH
except AttributeError:
    UPLOAD_CRAWLER_PATH = 'crawler/static/crawler/'
