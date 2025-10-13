from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Invoice
from .serializers import InvoiceSerializer, UserSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing invoices.
    Provides CRUD operations (Create, Read, Update, Delete) for invoices.
    Automatically handles:
    - Listing all invoices (GET /api/invoices/)
    - Creating new invoices (POST /api/invoices/)
    - Retrieving single invoice (GET /api/invoices/1/)
    - Updating invoices (PUT /api/invoices/1/)
    - Deleting invoices (DELETE /api/invoices/1/)
    """
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()

    def get_queryset(self):
        """
        Ensure users can only see their own invoices.
        This is for security and data isolation.
        """
        user = self.request.user
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        """
        Automatically assign the current user when creating an invoice.
        """
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def extract_information(self, request, pk=None):
        """
        Custom action to trigger invoice information extraction.
        This will be our main AI processing endpoint.
        Access via: POST /api/invoices/1/extract_information/
        """
        invoice = self.get_object()

        # TODO: Implement actual extraction logic here
        # For now, return a placeholder response
        return Response({
            "message": "Extraction endpoint ready - AI logic coming next!",
            "invoice_id": invoice.id,
            "status": "pending_implementation"
        })

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer