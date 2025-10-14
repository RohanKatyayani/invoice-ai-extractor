import pdfplumber
import PyPDF2
from typing import Optional
from .ocr_extractor import OCRExtractor  # ADD THIS


class PDFExtractor:
    """
    Handles text extraction from PDF invoices with OCR fallback
    """

    def __init__(self):
        self.ocr_extractor = OCRExtractor()  # ADD THIS

    def extract_text(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF file using multiple methods
        """
        text = ""

        # Method 1: Try pdfplumber first
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            print(f"✓ pdfplumber extracted {len(text)} characters")

            # Check if text looks reasonable (not garbled)
            if self._is_reasonable_text(text):
                return text
            else:
                print("⚠️  Text looks garbled, trying OCR...")
                text = ""  # Reset for OCR

        except Exception as e:
            print(f"✗ pdfplumber failed: {e}")

        # Method 2: If pdfplumber failed or got garbled text, try PyPDF2
        if not text.strip():
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                print(f"✓ PyPDF2 extracted {len(text)} characters")

                # Check if text looks reasonable
                if self._is_reasonable_text(text):
                    return text
                else:
                    print("⚠️  Text still garbled, trying OCR...")
                    text = ""  # Reset for OCR

            except Exception as e:
                print(f"✗ PyPDF2 failed: {e}")

        # Method 3: OCR fallback for scanned/image PDFs
        if not text.strip():
            print("🔄 Falling back to OCR...")
            ocr_text = self.ocr_extractor.extract_text_with_ocr(pdf_path)
            if ocr_text and self._is_reasonable_text(ocr_text):
                return ocr_text

        return text if text.strip() else None

    def _is_reasonable_text(self, text: str) -> bool:
        """
        Check if extracted text looks reasonable (not garbled OCR)
        """
        if not text or len(text.strip()) < 10:
            return False

        # Check for common English words that should appear in invoices
        common_words = ['invoice', 'bill', 'date', 'amount', 'total', 'due', 'number', 'customer']
        text_lower = text.lower()

        # Count how many common words appear
        matches = sum(1 for word in common_words if word in text_lower)

        # If we find at least 2 common words, text is probably reasonable
        return matches >= 2