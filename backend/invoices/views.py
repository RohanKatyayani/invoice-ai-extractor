from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Invoice
from .serializers import InvoiceSerializer
from .extraction import InvoiceProcessor
from django.shortcuts import render
from django.http import HttpResponse

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

def invoice_table(request):
    """Simple table view"""
    invoices = Invoice.objects.all()

    html = """
    <html>
    <style>
        table { border-collapse: collapse; width: 100%; margin: 20px; }
        th, td { border: 1px solid black; padding: 10px; text-align: left; }
        th { background: #f0f0f0; }
        tr:nth-child(even) { background: #f9f9f9; }
    </style>
    <body>
        <h1>📊 INVOICE DATA TABLE</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Invoice Number</th>
                <th>Amount</th>
                <th>Invoice Date</th>
                <th>Due Date</th>
                <th>Confidence</th>
            </tr>
    """

    for invoice in invoices:
        html += f"""
            <tr>
                <td>{invoice.id}</td>
                <td><strong>{invoice.invoice_number or 'Not Found'}</strong></td>
                <td>${invoice.amount or 'Not Found'}</td>
                <td>{invoice.invoice_date or 'Not Found'}</td>
                <td>{invoice.due_date or 'Not Found'}</td>
                <td>{invoice.confidence_score}</td>
            </tr>
        """

    html += f"""
        </table>
        <div style="margin: 20px;">
            <strong>Total Invoices: {invoices.count()}</strong>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)