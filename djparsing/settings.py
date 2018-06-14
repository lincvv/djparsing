# import os
import pathlib
# from django.conf import settings

# PATH_TEMP = os.path.join(os.path.abspath(os.curdir), 'temp')


PATH_TEMP = pathlib.Path.cwd().joinpath('temp')
