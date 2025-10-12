"""
URL configuration for invoice_extractor project.
This is like the "ROUTING TABLE" for our web application.
It tells Django which code to run when someone visits a specific URL.
"""
from django.urls import path
from django.http import HttpResponse

# Temporary view for testing - we'll replace this later
def home(request):
    """Simple home page to verify Django is working."""
    return HttpResponse("The Invoice Extraction API is running!")

urlpatterns = [
    # Route: when someone visits the root URL ('/'), show the home page
    path('', home, name='home'),
]