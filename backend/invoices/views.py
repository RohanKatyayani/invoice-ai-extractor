from .extraction.coordinator import ExtractionCoordinator
import tempfile
import os
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

    # DELETE the perform_create method entirely
    # Let the serializer handle user assignment

    @action(detail=True, methods=['post'])
    def extract_information(self, request, pk=None):
        """
        Extract information from the uploaded invoice using AI.

        This is where our AI magic happens!
        """
        invoice = self.get_object()

        try:
            # Check if invoice has a file
            if not invoice.original_file:
                return Response(
                    {"error": "No PDF file attached to this invoice"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            print(f"Starting AI extraction for invoice {invoice.id}...")

            # Get the actual file path
            file_path = invoice.original_file.path

            # Initialize our extraction coordinator
            coordinator = ExtractionCoordinator()

            # Process the invoice PDF
            extraction_result = coordinator.process_invoice(file_path)

            print(f"Extraction completed: {extraction_result}")

            # Update the invoice with extracted data
            invoice.invoice_date = extraction_result.get('invoice_date')
            invoice.invoice_number = extraction_result.get('invoice_number')
            invoice.amount = extraction_result.get('amount')
            invoice.due_date = extraction_result.get('due_date')
            invoice.extraction_method = extraction_result.get('extraction_method', 'failed')
            invoice.confidence_score = extraction_result.get('confidence_score', 0.0)
            invoice.raw_text = extraction_result.get('raw_text', '')

            # Save the updated invoice
            invoice.save()

            # Return the results
            return Response({
                "message": "Extraction completed successfully!",
                "extraction_method": invoice.extraction_method,
                "confidence_score": invoice.confidence_score,
                "extracted_data": {
                    "invoice_date": invoice.invoice_date,
                    "invoice_number": invoice.invoice_number,
                    "amount": invoice.amount,
                    "due_date": invoice.due_date,
                }
            })

        except Exception as e:
            print(f"Extraction failed: {str(e)}")
            return Response(
                {"error": f"Extraction failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer