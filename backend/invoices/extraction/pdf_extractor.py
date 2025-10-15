import pdfplumber
from typing import Optional


class PDFExtractor:
    """
    Simple PDF text extraction
    """

    def extract_text(self, pdf_path: str) -> Optional[str]:
        """Extract text using pdfplumber"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            print(f"📄 Extracted {len(text)} characters")
            return text if text.strip() else None

        except Exception as e:
            print(f"❌ PDF extraction failed: {e}")
            return None