from rest_framework import serializers
from .models import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    """
    Converts Invoice model instances to JSON and back.
    This serializer handles:
    - Converting database objects to API responses
    - Validating incoming API data
    - Controlling which fields are exposed via API
    """
    class Meta:
        model = Invoice
        fields = [
            'id',                 # Auto-generated ID
            'invoice_date',       # Extraction target
            'invoice_number',     # Extraction target
            'amount',             # Extraction target
            'due_date',           # Extraction target
            'original_file',      # Uploaded PDF
            'uploaded_at',        # Auto timestamp
            'extraction_method',  # LLM, regex, etc.
            'confidence_score',   # 0.0 to 1.0
        ]
        read_only_fields = [
            'id',
            'uploaded_at',
            'extraction_method',
            'confidence_score'
        ]

    def create(self, validated_data):
        """
        Simple create method - no user assignment needed
        """
        return super().create(validated_data)