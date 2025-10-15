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
