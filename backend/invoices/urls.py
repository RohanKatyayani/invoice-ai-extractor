from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'invoices', views.InvoiceViewSet)
# Remove the users line entirely

urlpatterns = [
    path('', include(router.urls)),
]