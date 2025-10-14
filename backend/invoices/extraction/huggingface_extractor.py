import os
import re
import json
from typing import Dict, Optional
from datetime import datetime


class HuggingFaceExtractor:
    """
    100% FREE local AI using HuggingFace transformers
    No API calls, no limits, completely offline
    """

    def __init__(self):
        self.nlp_pipeline = None
        self.bert_model = None
        self._setup_models()

    def _setup_models(self):
        """Lazy loading of models to save memory"""
        try:
            # We'll use a lightweight approach - load models only when needed
            print("🤖 HuggingFace models ready (will load on first use)")
        except Exception as e:
            print(f"❌ Model setup error: {e}")

    def extract_with_bert(self, text: str) -> Dict:
        """
        Use BERT-based models for intelligent extraction
        """
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
            import torch

            # Use a lightweight NER model
            ner_pipeline = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                tokenizer="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )

            # Extract entities from text
            entities = ner_pipeline(text)

            result = self._process_entities(entities, text)
            return result

        except Exception as e:
            print(f"❌ BERT extraction failed: {e}")
            return self._advanced_rule_based_extraction(text)

    def extract_with_layoutlm(self, text: str, image_path: Optional[str] = None) -> Dict:
        """
        Use LayoutLM for document structure understanding
        """
        try:
            # For now, use rule-based since LayoutLM requires image input
            # In production, we'd process the PDF as image
            return self._advanced_rule_based_extraction(text)

        except Exception as e:
            print(f"❌ LayoutLM extraction failed: {e}")
            return self._advanced_rule_based_extraction(text)

    def _advanced_rule_based_extraction(self, text: str) -> Dict:
        """
        Advanced rule-based extraction with pattern matching
        This is surprisingly effective for structured documents like invoices
        """
        print("🔍 Using advanced rule-based extraction...")

        result = {}

        # Clean the text
        text = self._clean_text(text)

        # Extract amount with multiple patterns
        amount = self._extract_amount(text)
        if amount:
            result['amount'] = amount

        # Extract dates with context awareness
        dates_info = self._extract_dates_with_context(text)
        if dates_info.get('invoice_date'):
            result['invoice_date'] = dates_info['invoice_date']
        if dates_info.get('due_date'):
            result['due_date'] = dates_info['due_date']

        # Extract invoice number with multiple patterns
        invoice_number = self._extract_invoice_number(text)
        if invoice_number:
            result['invoice_number'] = invoice_number

        print(f"✅ Rule-based found: {result}")
        return result

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Normalize line breaks
        text = text.replace('\n', ' ').replace('\r', ' ')
        return text

    def _extract_amount(self, text: str) -> Optional[float]:
        """Advanced amount extraction with multiple patterns"""
        amount_patterns = [
            r'Total Amount Due\s*[$\s]*(\d+\.?\d*)',
            r'Amount Due\s*[$\s]*(\d+\.?\d*)',
            r'Total\s*[$\s]*(\d+\.?\d*)',
            r'Balance Due\s*[$\s]*(\d+\.?\d*)',
            r'[\$](\d+\.?\d*)',
            r'USD\s*(\d+\.?\d*)',
        ]

        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount = float(match)
                    # Validate it's a reasonable amount (not a date or other number)
                    if 0.01 <= amount <= 1000000:  # Reasonable invoice range
                        return amount
                except ValueError:
                    continue
        return None

    def _extract_dates_with_context(self, text: str) -> Dict:
        """Extract dates with context awareness"""
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

        # Context-based assignment
        result = {}
        if dates_found:
            # Look for due date context
            due_date_patterns = [
                r'due date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'due on[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'pay by[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            ]

            for pattern in due_date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    due_date = self._parse_date(match.group(1))
                    if due_date:
                        result['due_date'] = due_date
                        # Remove from general dates
                        if due_date in dates_found:
                            dates_found.remove(due_date)
                        break

            # Assign remaining dates
            if dates_found:
                result['invoice_date'] = dates_found[0]
            if len(dates_found) > 1 and 'due_date' not in result:
                result['due_date'] = dates_found[1]

        return result

    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Advanced invoice number extraction"""
        invoice_patterns = [
            r'Invoice Number\s*[:#]?\s*([A-Z0-9-]+)',
            r'Invoice #\s*([A-Z0-9-]+)',
            r'INV-\s*([A-Z0-9-]+)',
            r'Bill Number\s*[:#]?\s*([A-Z0-9-]+)',
            r'Invoice ID\s*[:#]?\s*([A-Z0-9-]+)',
            r'Ref\.?\s*[:#]?\s*([A-Z0-9-]+)',
        ]

        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _process_entities(self, entities: list, text: str) -> Dict:
        """Process named entities from BERT"""
        result = {}

        # Extract dates from entities
        date_entities = [ent for ent in entities if ent['entity_group'] in ['DATE', 'TIME']]
        if date_entities:
            dates = [self._parse_date(ent['word']) for ent in date_entities]
            dates = [d for d in dates if d]
            if dates:
                result['invoice_date'] = dates[0]
                if len(dates) > 1:
                    result['due_date'] = dates[1]

        # Extract amounts from entities
        amount_entities = [ent for ent in entities if ent['entity_group'] in ['MONEY', 'CARDINAL']]
        for ent in amount_entities:
            try:
                amount = float(re.sub(r'[^\d.]', '', ent['word']))
                if 0.01 <= amount <= 1000000:
                    result['amount'] = amount
                    break
            except:
                continue

        return result

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse various date formats to YYYY-MM-DD"""
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