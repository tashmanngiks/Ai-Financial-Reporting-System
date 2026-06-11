# AI Financial Analytics System

A comprehensive end-to-end financial analytics system that processes structured JSON data and generates professional analytical reports.

## Architecture Overview

### System Components
- **Backend**: Django + Django REST Framework
- **Frontend**: Vue.js 3 + Composition API
- **Database**: PostgreSQL
- **Processing**: Async task processing with Celery
- **Caching**: Redis

### Core Features
1. **Data Ingestion**: JSON file upload and API input
2. **Metrics Engine**: Financial calculations and trend analysis
3. **Insight Engine**: AI-powered analysis using structured prompts
4. **Report Generator**: Professional consulting-style reports
5. **Interactive Dashboard**: Real-time visualization and export

## Data Structure Support

The system supports JSON data with:
- Time series data (QCDashboard)
- Current financial metrics (Dashboard)
- Risk and benchmark data (IncomeRisk)
- Financial breakdowns (Dupont)

## Quick Start

### Backend Setup
```bash
cd backend
.\setup_venv.ps1
.\venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

If PowerShell blocks activation the first time, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `POST /api/upload/` - Upload financial data
- `POST /api/analyze/` - Trigger analysis
- `GET /api/reports/{id}/` - Retrieve generated report
- `GET /api/reports/` - List all reports

## Report Sections

Generated reports include:
1. Executive Summary
2. Trend Analysis
3. Financial Performance
4. Risk Assessment
5. Benchmark Comparison
6. Recommendations

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Production Stack
- Django + Gunicorn + Nginx
- PostgreSQL database
- Redis caching
- Celery workers
