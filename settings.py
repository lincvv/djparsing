import os
from django.conf import settings

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ATTR_LIST_INIT = ['app', 'model']
PATH_TEMP = os.path.join(settings.MEDIA_ROOT, 'parser/temp')