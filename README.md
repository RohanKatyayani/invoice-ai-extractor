# InvoiceAI Extractor

An intelligent invoice processing system that uses AI to automatically extract key information from PDF invoices.

## 📊 Features
- AI-powered invoice data extraction
- Support for multiple invoice formats
- Confidence scoring for extractions
- Drag & drop interface
- MongoDB integration

## 🛠️ Tech Stack
- **Backend**: Django, MongoDB, BERT
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI**: BERT, Heuristics, Transformers, Regex patterns
  
## Security Setup

1. **Environment Configuration:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your settings

## Quick Start
```bash
# Backend
cd backend
pip install -r requirements.txt
python manage.py runserver

# Frontend  
cd frontend
python -m http.server 3000

## 🎯 Demo

### Screenshots:

| Clean Invoice Extraction | Complex Invoice Handling |
|--------------------------|--------------------------|
| ![Clean Invoice](https://via.placeholder.com/400x250/4CAF50/white?text=98%25+Confidence+Extraction) | ![Complex Invoice](https://via.placeholder.com/400x250/FF9800/white?text=70%25+Confidence+Partial+Extraction) |

| Drag & Drop Interface | Multiple Format Support |
|----------------------|------------------------|
| ![Upload Interface](https://via.placeholder.com/400x250/2196F3/white?text=Drag+%26+Drop+Upload) | ![Multi-Format](https://via.placeholder.com/400x250/9C27B0/white?text=Multiple+Invoice+Formats) |

### Live Demo:
Visit [Live Demo Link] to test the application with sample invoices.

*Note: For privacy reasons, actual invoice samples are not included in this repository.*
