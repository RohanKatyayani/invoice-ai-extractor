"""
WSGI config for invoice_extractor project.
WSGI = Web Server Gateway Interface
This is the standard that allows web servers to talk to Django.
Think of it as the "TRANSLATOR" between web server and Django.
"""
import os
from django.core.wsgi import get_wsgi_application

# Tell Django where to find settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_extractor.settings')

# Create the WSGI application - this is what the web server will use
application = get_wsgi_application()