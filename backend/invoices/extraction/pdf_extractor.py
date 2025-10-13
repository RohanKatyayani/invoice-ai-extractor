import pdfplumber
import PyPDF2
from typing import Optional

class PDFExtractor:
    """
    Handles text extraction from PDF invoices.
    Uses multiple methods for reliability:
    - pdfplumber: Better for modern PDFs
    - PyPDF2: Fallback for older PDFs
    """

    def extract_text(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF file using multiple methods for reliability.
        Args:
            pdf_path: Path to the PDF file
        Returns:
            Extracted text as string, or None if extraction fails
        """
        text = ""

        # Method 1: Try pdfplumber first (better for modern PDFs)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            print(f"✓ pdfplumber extracted {len(text)} characters")
        except Exception as e:
            print(f"✗ pdfplumber failed: {e}")

        # Method 2: If pdfplumber failed or got little text, try PyPDF2
        if not text.strip():
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                print(f"✓ PyPDF2 extracted {len(text)} characters")
            except Exception as e:
                print(f"✗ PyPDF2 failed: {e}")

        return text if text.strip() else None

    def test_extraction(self):
        """
        Test method to verify our PDF extraction works.
        We'll use this with our sample Comcast bill.
        """
        # We'll implement this after we set up file uploads
        pass