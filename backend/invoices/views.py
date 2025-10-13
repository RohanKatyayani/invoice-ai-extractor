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

    # def get_queryset(self):
    #     """
    #     Ensure users can only see their own invoices.
    #     This is for security and data isolation.
    #     """
    #     user = self.request.user
    #     return self.queryset.filter(user=user)

    def get_queryset(self):
        """
        Ensure users can only see their own invoices.
        Handle both authenticated users and anonymous users.
        """
        user = self.request.user

        # If user is authenticated, return their invoices
        if user.is_authenticated:
            return self.queryset.filter(user=user)
        else:
            # If user is not authenticated, return empty queryset
            return self.queryset.none()

    # def perform_create(self, serializer):
    #     """
    #     Automatically assign the current user when creating an invoice.
    #     """
    #     serializer.save(user=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically assign the current user when creating an invoice.
        Only allow creation for authenticated users.
        """
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            # If not authenticated, you might want to handle this differently
            # For now, we'll raise an error
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You must be logged in to create invoices")

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