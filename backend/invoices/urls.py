from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'invoices', views.InvoiceViewSet)
router.register(r'users', views.UserViewSet)

# API URL patterns
urlpatterns = [
    path('', include(router.urls)),
]