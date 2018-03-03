import os
from django.conf import settings
# from distutils import dirname

PATH_TEMP = os.path.join(settings.MEDIA_ROOT, 'temp')
# PATH_TEMP = os.path.join(dirname(__file__), 'temp')