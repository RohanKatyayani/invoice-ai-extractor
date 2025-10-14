import os
import tempfile
from typing import Optional

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("❌ OCR dependencies not installed. Run: pip install pytesseract pdf2image opencv-python")


class OCRExtractor:
    """
    OCR-based text extraction for scanned/image PDFs
    Uses Tesseract OCR to extract text from PDF images
    """

    def extract_text_with_ocr(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF using OCR (for scanned/image PDFs)
        """
        if not OCR_AVAILABLE:
            print("❌ OCR not available - install dependencies")
            return None

        try:
            print("🔍 Using OCR for scanned PDF...")

            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)

            # OCR each image
            full_text = ""
            for i, image in enumerate(images):
                print(f"📄 OCR processing page {i + 1}/{len(images)}...")

                # Preprocess image for better OCR
                processed_image = self._preprocess_image(image)

                # Extract text using Tesseract
                page_text = pytesseract.image_to_string(processed_image, lang='eng')
                full_text += page_text + "\n\n"

            print(f"✅ OCR extracted {len(full_text)} characters")
            return full_text if full_text.strip() else None

        except Exception as e:
            print(f"❌ OCR extraction failed: {e}")
            return None

    def _preprocess_image(self, image):
        """
        Preprocess image for better OCR accuracy
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')

        # You can add more preprocessing here:
        # - Noise removal
        # - Contrast enhancement
        # - Deskewing
        # - etc.

        return image