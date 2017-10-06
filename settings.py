import os
from mysite.settings import MEDIA_ROOT

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ATTR_LIST_INIT = ['app', 'model']
PATH_TEMP = os.path.join(MEDIA_ROOT, 'parser/temp')