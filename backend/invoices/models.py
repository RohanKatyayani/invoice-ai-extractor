from django.db import models
from django.contrib.auth.models import User

class Invoice(models.Model):
    """
    Database model to store extracted invoice information.

    This represents the core data we're extracting from PDF invoices:
    - Invoice date, number, amount, due date
    - File storage and metadata
    - Extraction method and confidence
    """

    # File information
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_file = models.FileField(upload_to='invoices/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Core extraction fields (what the assignment asks for)
    invoice_date = models.DateField(null=True, blank=True)
    invoice_number = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    # Extraction metadata
    extraction_method = models.CharField(max_length=50, default='pending')
    confidence_score = models.FloatField(default=0.0)
    raw_text = models.TextField(blank=True)  # Store extracted text for debugging

    def __str__(self):
        """String representation for admin and debugging."""
        return f"Invoice {self.invoice_number} - ${self.amount}"

    class Meta:
        """Metadata options for the model."""
        ordering = ['-uploaded_at']  # Newest invoices first