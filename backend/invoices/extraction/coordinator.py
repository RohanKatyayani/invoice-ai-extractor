from typing import Dict, Optional
from .pdf_extractor import PDFExtractor
from .llm_extractor import LLMExtractor
from .regex_extractor import RegexExtractor


class ExtractionCoordinator:
    """
    Coordinates between different extraction methods for best results.
    Strategy:
    1. Try AI extraction first (most accurate)
    2. If AI fails, use regex fallback
    3. Combine results intelligently
    4. Track confidence scores
    """

    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.llm_extractor = LLMExtractor()
        self.regex_extractor = RegexExtractor()

    def process_invoice(self, pdf_path: str) -> Dict:
        """
        Main method to process an invoice PDF and extract information.
        Args:
            pdf_path: Path to the PDF file
        Returns:
            Dictionary with extracted data and metadata
        """
        print(f"🚀 Starting extraction for: {pdf_path}")

        # Step 1: Extract text from PDF
        text = self.pdf_extractor.extract_text(pdf_path)
        if not text:
            return self._create_error_result("Could not extract text from PDF")

        print(f"📄 Extracted {len(text)} characters from PDF")

        # Step 2: Try AI extraction first
        ai_result = self.llm_extractor.extract_with_gpt(text)
        ai_valid = self.llm_extractor.validate_extraction(ai_result)

        if ai_valid:
            print("✅ AI extraction successful")
            return {
                **ai_result,
                'extraction_method': 'ai',
                'confidence_score': 0.9,
                'raw_text': text[:1000]  # Store first 1000 chars for reference
            }

        # Step 3: AI failed, try regex fallback
        print("AI extraction failed, trying regex fallback...")
        regex_result = self.regex_extractor.extract_information(text)

        if regex_result:
            print("✅ Regex extraction successful")
            return {
                **regex_result,
                'extraction_method': 'regex',
                'confidence_score': 0.7,
                'raw_text': text[:1000]
            }

        # Step 4: Both methods failed
        print("All extraction methods failed")
        return self._create_error_result("All extraction methods failed")

    def _create_error_result(self, error_message: str) -> Dict:
        """Create a standardized error result."""
        return {
            'invoice_date': None,
            'invoice_number': None,
            'amount': None,
            'due_date': None,
            'extraction_method': 'failed',
            'confidence_score': 0.0,
            'error': error_message
        }

    def test_with_sample(self, sample_text: str) -> Dict:
        """
        Test method to run extraction on sample text without PDF.
        Useful for development and testing.
        """
        print("Testing extraction with sample text...")

        # Try AI first
        ai_result = self.llm_extractor.extract_with_gpt(sample_text)
        ai_valid = self.llm_extractor.validate_extraction(ai_result)

        if ai_valid:
            return {**ai_result, 'method': 'ai'}

        # Fallback to regex
        regex_result = self.regex_extractor.extract_information(sample_text)
        if regex_result:
            return {**regex_result, 'method': 'regex'}

        return {'error': 'No data extracted', 'method': 'failed'}