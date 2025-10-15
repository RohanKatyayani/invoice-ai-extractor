from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Invoice
from .serializers import InvoiceSerializer
from .extraction import InvoiceProcessor

class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()

    @action(detail=True, methods=['post'])
    def extract_information(self, request, pk=None):
        """Extract information using BERT"""
        invoice = self.get_object()

        try:
            if not invoice.original_file:
                return Response(
                    {"error": "No PDF file attached"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            print(f"Starting BERT extraction for invoice {invoice.id}...")

            # Use simplified processor
            processor = InvoiceProcessor()
            file_path = invoice.original_file.path
            result = processor.process_invoice(file_path)

            print(f"BERT extraction completed: {result}")

            # Update invoice
            invoice.invoice_date = result.get('invoice_date')
            invoice.invoice_number = result.get('invoice_number')
            invoice.amount = result.get('amount')
            invoice.due_date = result.get('due_date')
            invoice.extraction_method = result.get('extraction_method', 'bert_extraction')
            invoice.confidence_score = result.get('confidence_score', 0.0)
            invoice.raw_text = result.get('raw_text', '')

            invoice.save()

            return Response({
                "message": "BERT extraction completed!",
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