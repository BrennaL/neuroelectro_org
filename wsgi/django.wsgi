import os
import sys

path = '/home/rgerkin'
if path not in sys.path:
   sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

import www.settings

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

