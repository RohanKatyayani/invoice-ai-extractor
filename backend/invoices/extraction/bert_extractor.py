import re
from typing import Dict, Optional
from datetime import datetime, timedelta
from dateutil import parser

class BERTExtractor:
    """
    SMART Invoice Extractor
    """

    def __init__(self):
        self.currency_symbols = self._get_all_currency_symbols()
        print(f"Loaded {len(self.currency_symbols)} currency symbols")

    def extract_information(self, text: str) -> Dict:
        """
        Smart extraction returning proper numeric types
        """
        result = {}

        # SMART EXTRACTION
        self._extract_amount_numeric(text, result)
        self._extract_invoice_number_comprehensive(text, result)
        self._extract_dates_universal(text, result)

        result['confidence_score'] = self._calculate_confidence(result)
        result['extraction_method'] = 'bert_extraction'

        return result

    def _get_all_currency_symbols(self):
        """Get all currency symbols"""
        symbols = set()

        symbols.update(['$', '€', '£', '¥', '₹', '₽', '₩', '₺', '₴', '₸', '₪', '₫', '₦', '₡', '₱'])
        symbols.update(['USD', 'EUR', 'GBP', 'INR', 'CAD', 'AUD', 'SGD', 'JPY', 'CNY', 'CHF', 'NZD'])
        symbols.update(['Rs', 'Rs.', 'RS', 'RS.'])

        return symbols

    def _extract_amount_numeric(self, text: str, result: Dict):
        """Extract amount as numeric value"""
        print("NUMERIC AMOUNT EXTRACTION...")

        currency_pattern = '|'.join(re.escape(symbol) for symbol in self.currency_symbols)

        currency_patterns = [
            rf'((?:{currency_pattern})\s*[\d,]+\.\d{{2}})',
            rf'((?:{currency_pattern})\s*[\d,]+)',
            rf'(Total[\s\S]{{0,100}}?(?:{currency_pattern})\s*[\d,]+\.\d{{2}})',
            rf'(Amount[\s\S]{{0,100}}?(?:{currency_pattern})\s*[\d,]+\.\d{{2}})',
        ]

        all_amounts = []

        for pattern in currency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for full_match in matches:
                print(f"Found formatted amount: '{full_match}'")

                numeric_value = self._extract_numeric_value(full_match)

                # FILTER OUT OBVIOUSLY WRONG AMOUNTS
                if numeric_value and 0.01 <= numeric_value <= 2000:  # Reasonable bill amount range
                    all_amounts.append((numeric_value, full_match.strip()))
                    print(f"Valid amount: {numeric_value}")
                else:
                    print(f"Rejected unreasonable amount: {numeric_value}")

        if all_amounts:
            largest_amount = max(all_amounts, key=lambda x: x[0])
            result['amount'] = largest_amount[0]
            result['amount_formatted'] = largest_amount[1]
            print(f"Selected amount: {result['amount_formatted']}")
        else:
            print("No currency amounts found")
            result['amount'] = None

    def _extract_numeric_value(self, formatted_amount: str) -> Optional[float]:
        """Extract numeric value from formatted amount string"""
        try:
            cleaned = re.sub(r'[$\€\£\¥\₹\₽\₩\₺\₴\₸\₪\₫\₦\₡\₱]', '', formatted_amount, flags=re.IGNORECASE)
            cleaned = re.sub(r'\b(USD|EUR|GBP|INR|CAD|AUD|SGD|JPY|CNY|CHF|NZD|Rs|Rs\.)\b', '', cleaned,
                             flags=re.IGNORECASE)
            cleaned = re.sub(r'\b(Total|Amount|Balance|Due|Subtotal)\b', '', cleaned, flags=re.IGNORECASE)

            numeric_match = re.search(r'([\d,]+\.\d{2}|[\d,]+)', cleaned.strip())
            if numeric_match:
                numeric_str = numeric_match.group(1).replace(',', '')
                return float(numeric_str)
        except:
            pass
        return None

    def _extract_invoice_number_comprehensive(self, text: str, result: Dict):
        """Simple invoice number extraction - just get what comes after Invoice #"""
        print("SIMPLE INVOICE NUMBER EXTRACTION...")

        # SIMPLEST PATTERNS - just get what comes after Invoice markers
        patterns = [
            r'Invoice\s*#\s*([A-Za-z0-9\-]+)',  # Invoice #1164006105
            r'INVOICE\s*#\s*([A-Za-z0-9\-]+)',  # INVOICE #1164006105
            r'Invoice\s*No\.?\s*:?\s*([A-Za-z0-9\-]+)',  # Invoice No: 1164006105
            r'Bill\s*#\s*([A-Za-z0-9\-]+)',  # Bill #1164006105
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                inv_num = match.group(1).strip()
                # Basic validation - just make sure it's not empty and looks like an invoice number
                if inv_num and len(inv_num) >= 3:
                    result['invoice_number'] = inv_num
                    print(f"Invoice number found: '{inv_num}'")
                    return

        print("No invoice number found")
        result['invoice_number'] = None

    def _extract_dates_universal(self, text: str, result: Dict):
        """Universal date extraction"""
        print("UNIVERSAL DATE EXTRACTION...")

        date_patterns = [
            r'\b\d{1,4}[-/\.]\d{1,2}[-/\.]\d{1,4}\b',
            r'\b\d{1,2}\s+[A-Za-z]+\s+\d{2,4}\b',
            r'\b[A-Za-z]+\s+\d{1,2},?\s+\d{4}\b',
        ]

        all_date_strings = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            all_date_strings.extend(matches)

        print(f"Found potential dates: {all_date_strings}")

        valid_dates = []
        for date_str in all_date_strings:
            try:
                parsed_date = parser.parse(date_str, fuzzy=True)
                valid_dates.append(parsed_date.strftime('%Y-%m-%d'))
                print(f"Parsed: '{date_str}' -> {parsed_date.strftime('%Y-%m-%d')}")
            except:
                continue

        if valid_dates:
            unique_dates = sorted(list(set(valid_dates)))
            if len(unique_dates) >= 2:
                result['invoice_date'] = unique_dates[0]
                result['due_date'] = unique_dates[-1]
            else:
                result['invoice_date'] = unique_dates[0]
                result['due_date'] = self._estimate_due_date(unique_dates[0])
        else:
            result['invoice_date'] = None
            result['due_date'] = None

    def _estimate_due_date(self, invoice_date: str) -> str:
        """Estimate due date"""
        try:
            invoice_dt = datetime.strptime(invoice_date, '%Y-%m-%d')
            due_dt = invoice_dt + timedelta(days=30)
            return due_dt.strftime('%Y-%m-%d')
        except:
            return invoice_date

    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence - SIMPLE AND WORKING"""
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