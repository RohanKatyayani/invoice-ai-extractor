import re
from typing import Dict, Optional
from datetime import datetime, timedelta
from dateutil import parser


class BERTExtractor:
    """
    SMART Invoice Extractor with BERT Validation + Fallback
    """
    def __init__(self):
        self.currency_symbols = self._get_all_currency_symbols()
        self.bert_ner = None

        try:
            from transformers import pipeline
            self.bert_ner = pipeline(
                "token-classification",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
            print("BERT Model Loaded Successfully!")
        except Exception as e:
            print(f"BERT loading failed: {e}. Using reliable regex fallback.")

        print(f"Loaded {len(self.currency_symbols)} currency symbols")

    def extract_information(self, text: str) -> Dict:
        """
        Smart extraction with BERT validation + reliable fallback
        """
        result = {}

        # PHASE 1: ALWAYS USE PROVEN REGEX FOR AMOUNTS AND DATES
        self._extract_amount_numeric(text, result)
        self._extract_dates_universal(text, result)

        # PHASE 2: INTELLIGENT INVOICE NUMBER EXTRACTION
        self._extract_invoice_number_intelligent(text, result)

        result['confidence_score'] = self._calculate_confidence(result)
        result['extraction_method'] = 'bert_extraction'
        result['bert_available'] = self.bert_ner is not None

        return result

    def _extract_invoice_number_intelligent(self, text: str, result: Dict):
        """Intelligent invoice number extraction with multiple fallbacks"""
        print("INTELLIGENT INVOICE NUMBER EXTRACTION...")

        # METHOD 1: Try BERT-validated extraction first (if available)
        if self.bert_ner:
            bert_result = self._extract_with_bert_validation(text)
            if bert_result:
                result['invoice_number'] = bert_result
                result['bert_validated'] = True
                result['extraction_method'] = 'bert_validated'
                print(f"BERT-VALIDATED Invoice Number: '{bert_result}'")
                return

        # METHOD 2: Fallback to proven regex patterns
        regex_result = self._extract_with_regex_fallback(text)
        if regex_result:
            result['invoice_number'] = regex_result
            result['bert_validated'] = False
            result['extraction_method'] = 'regex_fallback'
            print(f"REGEX Fallback Invoice Number: '{regex_result}'")
            return

        # METHOD 3: Final fallback - look for any invoice-like patterns
        final_result = self._extract_with_context_analysis(text)
        if final_result:
            result['invoice_number'] = final_result
            result['bert_validated'] = False
            result['extraction_method'] = 'context_analysis'
            print(f"Context Analysis Invoice Number: '{final_result}'")
            return

        print("No invoice number found with any method")
        result['invoice_number'] = None

    def _extract_with_bert_validation(self, text: str) -> Optional[str]:
        """Try to extract and validate with BERT"""
        if not self.bert_ner:
            return None

        try:
            # Use BERT to find all entities
            entities = self.bert_ner(text)

            # Look for invoice-like entities
            for entity in entities:
                entity_text = entity['word'].strip()
                # Check if this looks like an invoice number
                if self._looks_like_invoice_number(entity_text):
                    print(f"BERT found potential: '{entity_text}' as {entity['entity_group']}")
                    return entity_text

        except Exception as e:
            print(f"BERT extraction failed: {e}")

        return None

    def _extract_with_regex_fallback(self, text: str) -> Optional[str]:
        """Reliable regex patterns from original working code"""
        patterns = [
            r'Invoice\s*#\s*([A-Za-z0-9\-]+)',            # Invoice #1164006105
            r'INVOICE\s*#\s*([A-Za-z0-9\-]+)',            # INVOICE #1164006105
            r'Invoice\s*No\.?\s*:?\s*([A-Za-z0-9\-]+)',   # Invoice No: 1164006105
            r'Bill\s*#\s*([A-Za-z0-9\-]+)',               # Bill #1164006105
            r'Invoice\s*Number\s*:?\s*([A-Za-z0-9\-]+)',  # Invoice Number: INV-001
            r'INV-\d+',                                   # INV-12345
            r'Bill\s*Number\s*:?\s*([A-Za-z0-9\-]+)',     # Bill Number: 123
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                inv_num = match.group(1) if match.groups() else match.group(0)
                inv_num = inv_num.strip()
                if inv_num and len(inv_num) >= 3:
                    print(f"Regex found: '{inv_num}' with pattern: {pattern}")
                    return inv_num
        return None

    def _extract_with_context_analysis(self, text: str) -> Optional[str]:
        """Final fallback - look for any number near invoice keywords"""
        invoice_keywords = ['invoice', 'bill', 'inv', 'number', 'no', '#']

        # Look for numbers near invoice-related words
        for keyword in invoice_keywords:
            pattern = rf'{keyword}[^\d]*(\d{{4,10}})'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                potential_number = match.group(1)
                if self._looks_like_invoice_number(potential_number):
                    print(f"🔍 Context found: '{potential_number}' near '{keyword}'")
                    return potential_number
        return None

    def _looks_like_invoice_number(self, text: str) -> bool:
        """Check if text looks like a reasonable invoice number"""
        if not text or len(text) < 3:
            return False

        # Should be alphanumeric
        if not re.match(r'^[A-Za-z0-9\-_]+$', text):
            return False

        # Common words to exclude
        common_words = {'date', 'amount', 'total', 'page', 'number', 'invoice', 'bill'}
        if text.lower() in common_words:
            return False

        return True

    def _get_all_currency_symbols(self):
        """Get all currency symbols"""
        symbols = set()

        symbols.update(['$', '€', '£', '¥', '₹', '₽', '₩', '₺', '₴', '₸', '₪', '₫', '₦', '₡', '₱'])
        symbols.update(['USD', 'EUR', 'GBP', 'INR', 'CAD', 'AUD', 'SGD', 'JPY', 'CNY', 'CHF', 'NZD'])
        symbols.update(['Rs', 'Rs.', 'RS', 'RS.'])

        return symbols

    def _extract_amount_numeric(self, text: str, result: Dict):
        """PROVEN AMOUNT EXTRACTION - Never fails"""
        print("💰 RELIABLE AMOUNT EXTRACTION...")

        currency_pattern = '|'.join(re.escape(symbol) for symbol in self.currency_symbols)

        # PRIORITIZE DECIMAL AMOUNTS FIRST
        currency_patterns = [
            rf'((?:{currency_pattern})\s*[\d,]+\.\d{{2}})',
            rf'(Total[\s\S]{{0,100}}?(?:{currency_pattern})\s*[\d,]+\.\d{{2}})',
            rf'(Amount[\s\S]{{0,100}}?(?:{currency_pattern})\s*[\d,]+\.\d{{2}})',
            rf'(Amount Due[\s\S]{{0,100}}?(?:{currency_pattern})\s*[\d,]+\.\d{{2}})',
            # Fallback to amounts without decimals
            rf'((?:{currency_pattern})\s*[\d,]+)',
        ]

        all_amounts = []

        for pattern in currency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for full_match in matches:
                print(f"Found amount: '{full_match}'")

                numeric_value = self._extract_numeric_value(full_match)
                if numeric_value and 0.01 <= numeric_value <= 2000:
                    all_amounts.append((numeric_value, full_match.strip()))
                    print(f"Valid amount: {numeric_value}")

        if all_amounts:
            largest_amount = max(all_amounts, key=lambda x: x[0])
            result['amount'] = largest_amount[0]
            result['amount_formatted'] = largest_amount[1]
            print(f"Selected amount: {result['amount_formatted']}")
        else:
            print("No valid amounts found")
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

    def _extract_dates_universal(self, text: str, result: Dict):
        """PROVEN DATE EXTRACTION - Never fails"""
        print("RELIABLE DATE EXTRACTION...")

        date_patterns = [
            r'\b\d{1,4}[-/\.]\d{1,2}[-/\.]\d{1,4}\b',
            r'\b\d{1,2}\s+[A-Za-z]+\s+\d{2,4}\b',
            r'\b[A-Za-z]+\s+\d{1,2},?\s+\d{4}\b',
        ]

        all_date_strings = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            all_date_strings.extend(matches)

        print(f"Found dates: {all_date_strings}")

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
        """Calculate confidence"""
        score = 0.0
        if result.get('amount'):
            score += 0.4
        if result.get('invoice_number'):
            score += 0.3
            # Bonus for BERT validation
            if result.get('bert_validated'):
                score += 0.1
        if result.get('invoice_date'):
            score += 0.2
        if result.get('due_date'):
            score += 0.1

        return max(0.1, min(0.98, score))