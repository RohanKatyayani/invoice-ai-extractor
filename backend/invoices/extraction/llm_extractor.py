import os
import json
import requests
from typing import Dict, Optional
from django.conf import settings


class LLMExtractor:
    """
    AI-powered extraction using OpenAI GPT to find invoice information.
    This is the core AI logic that will:
    1. Take extracted text from PDF
    2. Use GPT to find specific fields
    3. Return structured data
    """

    def __init__(self):
        # We'll set up API key properly later
        self.api_key = os.getenv('OPENAI_API_KEY', 'your-api-key-here')

    def extract_with_gpt(self, text: str) -> Dict:
        """
        Use OpenAI GPT to extract invoice information from text.
        Args:
            text: Raw text extracted from PDF invoice
        Returns:
            Dictionary with extracted fields or empty dict if failed
        """
        # Limit text to avoid token limits
        limited_text = text[:3000]  # First 3000 characters

        prompt = f"""
        Extract the following information from this invoice text:
        - Invoice date (format: YYYY-MM-DD)
        - Invoice number
        - Total amount (just the number, no currency symbol)
        - Due date (format: YYYY-MM-DD)

        Return ONLY a JSON object with these keys: invoice_date, invoice_number, amount, due_date
        If you cannot find a field, use null.

        Invoice Text:
        {limited_text}

        JSON Response:
        """
        # For now, return mock data since we don't have API key yet
        # We'll implement actual API call in next step
        return self._mock_extraction(limited_text)

    def _mock_extraction(self, text: str) -> Dict:
        """
        Mock extraction for testing without real API key.
        This helps us test our pipeline while we set up the real API.
        """
        print("🔧 Using mock extraction (no API key yet)")
        # Simple pattern matching as mock logic
        mock_data = {
            "invoice_date": "2015-12-12",  # From the Comcast sample
            "invoice_number": "SAMPLE-001",
            "amount": 108.82,  # From the Comcast sample
            "due_date": "2016-01-12"  # From the Comcast sample
        }

        return mock_data

    def validate_extraction(self, data: Dict) -> bool:
        """
        Validate that extracted data has at least some useful information.
        """
        if not data:
            return False

        # Check if we have at least one meaningful field
        meaningful_fields = 0
        if data.get('invoice_date'):
            meaningful_fields += 1
        if data.get('invoice_number'):
            meaningful_fields += 1
        if data.get('amount'):
            meaningful_fields += 1
        if data.get('due_date'):
            meaningful_fields += 1

        return meaningful_fields >= 2  # At least 2 fields found