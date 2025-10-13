from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Invoice Extraction API is running!")

urlpatterns = [
    path('', home, name='home'),
    path('api/', include('invoices.urls')),
]