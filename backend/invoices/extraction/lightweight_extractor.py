import re
import json
from typing import Dict, Optional  # ADD THIS IMPORT!
from datetime import datetime


class LightweightExtractor:
    """
    Lightweight but intelligent extraction using advanced patterns
    No heavy AI dependencies needed
    """

    def extract_information(self, text: str) -> Dict:
        """
        Intelligent extraction using context-aware pattern matching
        """
        print("🔍 Using intelligent pattern-based extraction...")

        # Clean and normalize text
        text = self._clean_text(text)

        result = {}

        # Extract amount with context
        amount = self._extract_amount_with_context(text)
        if amount:
            result['amount'] = amount

        # Extract dates with intelligent assignment
        dates_info = self._extract_dates_intelligently(text)
        result.update(dates_info)

        # Extract invoice number
        invoice_number = self._extract_invoice_number_advanced(text)
        if invoice_number:
            result['invoice_number'] = invoice_number

        # Calculate confidence based on how many fields we found
        confidence = self._calculate_confidence(result)
        result['confidence'] = confidence

        print(f"✅ Extraction results: {result}")
        return result

    def _clean_text(self, text: str) -> str:
        """Clean text for better pattern matching"""
        # Normalize spaces and line breaks
        text = ' '.join(text.split())
        # Common OCR fixes
        text = text.replace('|', 'I').replace('0', 'O')  # Common OCR errors
        return text

    def _extract_amount_with_context(self, text: str) -> Optional[float]:
        """Extract amount with context awareness - IMPROVED VERSION"""
        # Priority patterns (most reliable) - EXPANDED
        priority_patterns = [
            r'Total Amount Due\s*[$\s~]*(\d+[.,]?\d*)',
            r'Amount Due\s*[$\s~]*(\d+[.,]?\d*)',
            r'Balance Due\s*[$\s~]*(\d+[.,]?\d*)',
            r'Total Due\s*[$\s~]*(\d+[.,]?\d*)',
            r'Total New Charges\s*[$\s~]*(\d+[.,]?\d*)',
            r'Total\s*[$\s~]*(\d+[.,]?\d*)',
            r'Total Amount\s*[~]?\s*(\d+[.,]?\d*)',  # Porter specific
            r'Net Fare\s*[=]?\s*(\d+[.,]?\d*)',  # Porter specific
            r'Net Amount\s*[=]?\s*(\d+[.,]?\d*)',  # General
        ]

        for pattern in priority_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '').replace('~', '')
                try:
                    amount = float(amount_str)
                    if self._is_reasonable_amount(amount):
                        print(f"💰 Found amount: {amount} with pattern: {pattern}")
                        return amount
                except ValueError:
                    continue

        # Look for dollar amounts in common positions
        dollar_patterns = [
            r'[\$](\d+[.,]?\d*)',
            r'USD\s*(\d+[.,]?\d*)',
        ]

        # Get all dollar amounts and take the largest (usually the total)
        all_amounts = []
        for pattern in dollar_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.replace(',', '')
                try:
                    amount = float(amount_str)
                    if self._is_reasonable_amount(amount):
                        all_amounts.append(amount)
                except ValueError:
                    continue

        if all_amounts:
            # Return the largest amount (usually the total)
            largest_amount = max(all_amounts)
            print(f"💰 Found largest amount: {largest_amount}")
            return largest_amount

        return None

    def _extract_dates_intelligently(self, text: str) -> Dict:
        """Intelligently extract and assign dates - IMPROVED"""
        dates_found = self._find_all_dates(text)
        result = {}

        if not dates_found:
            return result

        # Look for explicit date labels first
        explicit_dates = self._find_explicit_dates(text, dates_found)
        if explicit_dates:
            result.update(explicit_dates)
            # Remove found dates from the general list
            for date in explicit_dates.values():
                if date in dates_found:
                    dates_found.remove(date)

        # Assign remaining dates logically
        if not result.get('invoice_date') and dates_found:
            result['invoice_date'] = dates_found[0]
        if len(dates_found) > 1 and not result.get('due_date'):
            result['due_date'] = dates_found[1]

        return result

    def _find_explicit_dates(self, text: str, dates_found: list) -> Dict:
        """Find dates with explicit labels"""
        result = {}

        # Date patterns with labels
        date_patterns = [
            (r'Date\s*[:]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', 'invoice_date'),
            (r'Invoice Date\s*[:]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', 'invoice_date'),
            (r'Due Date\s*[:]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', 'due_date'),
            (r'Bill Date\s*[:]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', 'invoice_date'),
        ]

        for pattern, field_name in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                found_date = self._parse_date(match.group(1))
                if found_date and found_date in dates_found:
                    result[field_name] = found_date

        return result

    def _find_all_dates(self, text: str) -> list:
        """Find all valid dates in text"""
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
            r'(\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
        ]

        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match[0] if isinstance(match, tuple) else match
                parsed_date = self._parse_date(date_str)
                if parsed_date and parsed_date not in dates_found:
                    dates_found.append(parsed_date)

        return sorted(dates_found)  # Sort chronologically

    def _find_due_date_by_context(self, text: str, dates_found: list) -> Optional[str]:
        """Find due date using context patterns"""
        due_context_patterns = [
            r'due date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'due on[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'pay by[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'payment due[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'auto pay[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]

        for pattern in due_context_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                due_date = self._parse_date(match.group(1))
                if due_date and due_date in dates_found:
                    return due_date

        return None

    def _find_invoice_date_by_context(self, text: str, dates_found: list) -> Optional[str]:
        """Find invoice date using context patterns"""
        invoice_context_patterns = [
            r'invoice date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'bill date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'date issued[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'billing date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]

        for pattern in invoice_context_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_date = self._parse_date(match.group(1))
                if invoice_date and invoice_date in dates_found:
                    return invoice_date

        return None

    def _extract_invoice_number_advanced(self, text: str) -> Optional[str]:
        """Advanced invoice number extraction"""
        invoice_patterns = [
            r'Invoice Number\s*[:#]?\s*([A-Z0-9-]{3,20})',
            r'Invoice #\s*([A-Z0-9-]{3,20})',
            r'INV-\s*([A-Z0-9-]{3,20})',
            r'Bill Number\s*[:#]?\s*([A-Z0-9-]{3,20})',
            r'Invoice ID\s*[:#]?\s*([A-Z0-9-]{3,20})',
            r'Ref\.?\s*[:#]?\s*([A-Z0-9-]{3,20})',
            r'Account Number\s*[:#]?\s*([A-Z0-9-]{3,20})',
        ]

        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to YYYY-MM-DD format"""
        try:
            formats = [
                '%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d/%m/%Y',
                '%d %b %Y', '%d %B %Y', '%b %d, %Y', '%B %d, %Y'
            ]
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        except:
            pass
        return None

    def _is_reasonable_amount(self, amount: float) -> bool:
        """Check if amount is reasonable for an invoice"""
        return 0.01 <= amount <= 1000000

    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence score based on extracted fields"""
        fields_found = sum(1 for value in result.values() if value is not None and value != '')
        total_fields = 4  # invoice_date, invoice_number, amount, due_date

        base_confidence = fields_found / total_fields

        # Bonus for finding critical fields
        if result.get('amount'):
            base_confidence += 0.1
        if result.get('invoice_date') and result.get('due_date'):
            base_confidence += 0.1

        return min(0.95, base_confidence)  # Cap at 95%