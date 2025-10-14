# InvoiceAI Extractor

An intelligent invoice processing system that uses AI to automatically extract key information from PDF invoices.

## Features
- PDF invoice upload
- AI-powered data extraction (Invoice Date, Number, Amount, Due Date)
- RESTful API
- Web interface

## Tech Stack
- Backend: Django REST Framework
- AI: OpenAI GPT + Traditional NLP
- Frontend: React
- Database: PostgreSQL

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
npm install
npm start
