from .bert_extractor import BERTExtractor
from .pdf_extractor import PDFExtractor
from decimal import Decimal

class InvoiceProcessor:
    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.bert_extractor = BERTExtractor()

    def process_invoice(self, pdf_path: str) -> dict:
        """Main processing function"""
        print(f"Processing: {pdf_path}")

        # Extract text
        text = self.pdf_extractor.extract_text(pdf_path)
        if not text:
            return self._create_error_result("No text extracted")

        # Extract information with BERT
        result = self.bert_extractor.extract_information(text)

        return {
            'invoice_date': result.get('invoice_date'),
            'invoice_number': result.get('invoice_number'),
            'amount': result.get('amount'),
            'due_date': result.get('due_date'),
            'extraction_method': 'bert_extraction',
            'confidence_score': result.get('confidence_score', 0.0),  # ONLY CHANGE: confidence -> confidence_score
            'raw_text': text[:1000]  # Store first 1000 chars
        }

    def _create_error_result(self, error: str) -> dict:
        return {
            'invoice_date': None,
            'invoice_number': None,
            'amount': None,
            'due_date': None,
            'extraction_method': 'failed',
            'confidence_score': 0.0,
            'error': error,
            'raw_text': ''
        }