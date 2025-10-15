import re
from typing import Dict, Optional
from datetime import datetime, timedelta


class BERTExtractor:
    """
    Invoice Extractor
    """
    def __init__(self):
        pass

    def extract_information(self, text: str) -> Dict:
        """
        Extraction logic
        """
        result = {}

        # BASIC EXTRACTION
        self._extract_simple_amount(text, result)
        self._extract_simple_invoice_number(text, result)
        self._extract_simple_dates(text, result)

        result['confidence'] = self._calculate_confidence(result)

        return result

    def _extract_simple_amount(self, text: str, result: Dict):
        """Simple amount extraction - find ALL dollar amounts"""
        # Find ALL dollar amounts in the text
        dollar_matches = re.findall(r'[\$](\d+\.\d{2})', text)
        if dollar_matches:
            try:
                # Convert to floats and take the largest one (usually the total)
                amounts = [float(x) for x in dollar_matches]
                result['amount'] = max(amounts)
            except:
                pass

        # If no dollar amounts, look for numbered amounts
        if not result.get('amount'):
            numbered_matches = re.findall(r'Total Amount[\D]*(\d+\.\d{2})', text, re.IGNORECASE)
            if numbered_matches:
                try:
                    result['amount'] = float(numbered_matches[0])
                except:
                    pass

    def _extract_simple_invoice_number(self, text: str, result: Dict):
        """Simple invoice number extraction - only clean matches"""
        patterns = [
            r'Invoice No:\s*([A-Z]\d+\-[A-Z]+\-\d+)',  # Complex
            r'Invoice\s*#\s*(\d{2,})',                 # Simple invoices
            r'INVOICE\s*#\s*(\d{2,})',                 # Uppercase
            r'#\s*(\d{3,})',                           # Simple
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                inv_num = match.group(1)
                # Basic check - not too short
                if inv_num and len(inv_num) >= 2:
                    result['invoice_number'] = inv_num
                    return

        # If no invoice number found, leave it as None (will show "Not found")

    def _extract_simple_dates(self, text: str, result: Dict):
        """Simple date extraction"""
        dates_found = []
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',      # YYYY-MM-DD
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
            r'(\d{1,2}/\d{1,2}/\d{2})',  # MM/DD/YY
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                parsed = self._parse_date(match)
                if parsed:
                    dates_found.append(parsed)

        if dates_found:
            unique_dates = sorted(list(set(dates_found)))
            result['invoice_date'] = unique_dates[0]
            if len(unique_dates) > 1:
                result['due_date'] = unique_dates[-1]
            else:
                result['due_date'] = self._estimate_due_date(unique_dates[0])

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date"""
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y']
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                if fmt == '%m/%d/%y' and date_obj.year > 2025:
                    date_obj = date_obj.replace(year=date_obj.year - 100)
                return date_obj.strftime('%Y-%m-%d')
            except:
                continue
        return None

    def _estimate_due_date(self, invoice_date: str) -> str:
        """Estimate due date"""
        try:
            invoice_dt = datetime.strptime(invoice_date, '%Y-%m-%d')
            due_dt = invoice_dt + timedelta(days=30)
            return due_dt.strftime('%Y-%m-%d')
        except:
            return invoice_date

    def _clean_text(self, text: str) -> str:
        """Clean text"""
        text = ' '.join(text.split())
        return text

    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence"""
        score = 0.0
        if result.get('amount'):
            score += 0.4
        if result.get('invoice_number'):
            score += 0.3
        if result.get('invoice_date'):
            score += 0.2
        if result.get('due_date'):
            score += 0.1

        return max(0.1, min(0.98, score))