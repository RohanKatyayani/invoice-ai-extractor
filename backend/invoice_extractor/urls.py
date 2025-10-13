"""
URL configuration for invoice_extractor project.
"""
from django.urls import path, include
from django.http import HttpResponse


def home(request):
    """Simple home page to verify Django is working."""
    return HttpResponse("🎯 Invoice Extraction API is running!")


urlpatterns = [
    # Home page
    path('', home, name='home'),

    # API routes - all API endpoints will be under /api/
    path('api/', include('invoices.urls')),
]