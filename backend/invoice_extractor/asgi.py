"""
ASGI config for invoice_extractor project.
ASGI = Asynchronous Server Gateway Interface
This is the newer standard that supports async features.
We include it for future compatibility.
"""
import os
from django.core.asgi import get_asgi_application

# Tell Django where to find settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_extractor.settings')

# Create the ASGI application
application = get_asgi_application()