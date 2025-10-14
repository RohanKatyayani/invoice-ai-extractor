import torch
from transformers import pipeline
import json
import re
import os
from typing import Dict, Optional
from datetime import datetime


class FreeAIExtractor:
    """
    Free AI extraction using LOCAL TinyLlama model
    """

    def __init__(self):
        self.local_client = None
        self.load_local_model()

    def load_local_model(self):
        """Load TinyLlama locally - no API needed"""
        try:
            print("🔥 Loading TinyLlama 1.1B locally...")
            self.local_client = pipeline(
                "text-generation",
                model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            print("✅ Local AI model ready!")
        except Exception as e:
            print(f"❌ Local model load failed: {e}")
            self.local_client = None

    def extract_with_groq(self, text: str) -> Dict:
        """
        Use LOCAL AI instead of Groq API
        """
        # If local model is loaded, use it
        if self.local_client:
            try:
                return self._extract_with_local_ai(text)
            except Exception as e:
                print(f"❌ Local AI error: {e}")

        # Fallback to rule-based extraction
        return self._rule_based_extraction(text)

    def _extract_with_local_ai(self, text: str) -> Dict:
        """Extract using local TinyLlama model"""
        limited_text = text[:1500]

        prompt = f"""
        <|system|>
        Extract invoice information and return ONLY JSON with keys: invoice_date, invoice_number, amount, due_date
        Use format: {{"invoice_date": "YYYY-MM-DD", "invoice_number": "string", "amount": 100.50, "due_date": "YYYY-MM-DD"}}
        Return null for missing values.
        </s>
        <|user|>
        Text: {limited_text}
        </s>
        <|assistant|>
        {{"
        """

        try:
            response = self.local_client(
                prompt,
                max_new_tokens=200,
                temperature=0.1,
                do_sample=False,
                pad_token_id=self.local_client.tokenizer.eos_token_id
            )[0]['generated_text']

            # Extract JSON from response
            result_text = response[response.find('{'):response.find('}') + 1]
            result_text = self._clean_json_response(result_text)
            return json.loads(result_text)

        except Exception as e:
            print(f"Local AI parsing failed: {e}")
            return self._rule_based_extraction(text)

    def extract_with_huggingface(self, text: str) -> Dict:
        """
        Keep this as backup - but now uses local model primarily
        """
        return self.extract_with_groq(text)  # Now both methods use local AI

    # KEEP ALL YOUR EXISTING METHODS - THEY ARE PERFECT
    def _rule_based_extraction(self, text: str) -> Dict:
        # YOUR EXISTING CODE - DON'T CHANGE
        import re
        from datetime import datetime

        result = {}

        # Extract amount patterns
        amount_patterns = [
            r'Total Amount Due\s*[\$]?\s*(\d+\.?\d*)',
            r'Amount Due\s*[\$]?\s*(\d+\.?\d*)',
            r'Total\s*[\$]?\s*(\d+\.?\d*)',
            r'[\$](\d+\.?\d*)'
        ]

        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result['amount'] = float(match.group(1))
                    break
                except ValueError:
                    continue

        # Extract dates
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
        ]

        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match[0] if isinstance(match, tuple) else match
                parsed_date = self._parse_date(date_str)
                if parsed_date and parsed_date not in dates_found:
                    dates_found.append(parsed_date)

        if len(dates_found) >= 1:
            result['invoice_date'] = dates_found[0]
        if len(dates_found) >= 2:
            result['due_date'] = dates_found[1]

        # Extract invoice number
        invoice_patterns = [
            r'Invoice Number\s*[:]?\s*([A-Z0-9-]+)',
            r'Invoice #\s*([A-Z0-9-]+)',
            r'INV-\s*([A-Z0-9-]+)',
            r'Bill Number\s*[:]?\s*([A-Z0-9-]+)',
        ]

        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['invoice_number'] = match.group(1)
                break

        return result

    def _clean_json_response(self, text: str) -> str:
        """Clean AI response to ensure valid JSON"""
        # Remove markdown code blocks
        text = text.replace('```json', '').replace('```', '')
        text = text.strip()

        # Ensure it starts with { and ends with }
        if not text.startswith('{'):
            text = '{' + text
        if not text.endswith('}'):
            text = text + '}'

        return text

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse various date formats to YYYY-MM-DD"""
        from datetime import datetime

        try:
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