import re
from datetime import datetime
from typing import Dict, Optional

class RegexExtractor:
    """
    Traditional NLP using regular expressions as fallback when AI fails.
    Uses pattern matching to find:
    - Dates in various formats
    - Currency amounts
    - Invoice numbers
    - Due dates
    """
    def extract_information(self, text: str) -> Dict:
        """
        Use regex patterns to find invoice information.
        Args:
            text: Raw text from PDF invoice
        Returns:
            Dictionary with any found fields
        """
        result = {}

        print("🔍 Using regex fallback extraction...")

        # Extract amount (looking for currency patterns)
        amount = self._extract_amount(text)
        if amount:
            result['amount'] = amount

        # Extract dates
        dates = self._extract_dates(text)
        if len(dates) >= 1:
            result['invoice_date'] = dates[0]
        if len(dates) >= 2:
            result['due_date'] = dates[1]

        # Extract invoice number
        invoice_number = self._extract_invoice_number(text)
        if invoice_number:
            result['invoice_number'] = invoice_number

        print(f"🔍 Regex found: {result}")
        return result

    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract total amount from text."""
        amount_patterns = [
            r'Total Amount Due\s*[\$]?\s*(\d+\.?\d*)',
            r'Amount Due\s*[\$]?\s*(\d+\.?\d*)',
            r'Total\s*[\$]?\s*(\d+\.?\d*)',
            r'[\$](\d+\.?\d*)'  # General currency pattern

        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return None

    def _extract_dates(self, text: str) -> list:
        """Extract and parse dates from text."""
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',  # DD MMM YYYY
        ]

        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match[0] if isinstance(match, tuple) else match
                parsed_date = self._parse_date(date_str)
                if parsed_date and parsed_date not in dates_found:
                    dates_found.append(parsed_date)

        return dates_found

    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number from text."""
        invoice_patterns = [
            r'Invoice Number\s*[:]?\s*([A-Z0-9-]+)',
            r'Invoice #\s*([A-Z0-9-]+)',
            r'INV-\s*([A-Z0-9-]+)',
            r'Bill Number\s*[:]?\s*([A-Z0-9-]+)',
        ]

        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Convert various date formats to YYYY-MM-DD."""
        try:
            # Try different date formats
            formats = ['%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d/%m/%Y', '%d %b %Y']
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        except:
            pass
        return None