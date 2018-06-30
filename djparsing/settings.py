import os
import sys
import pathlib
# from django.conf import settings

if int(sys.version_info.minor) < 6:
    PATH_TEMP = os.path.join(os.path.abspath(os.curdir), 'temp')
else:
    PATH_TEMP = pathlib.Path.cwd().joinpath('temp')
