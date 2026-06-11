# Getting Started Guide

This guide will walk you through setting up and running the AI Financial Analytics System on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker & Docker Compose** (Recommended)
- **Python 3.11+** (for manual setup)
- **Node.js 18+** (for manual setup)
- **PostgreSQL 15+** (for manual setup)
- **Redis 7+** (for manual setup)
- **Git**

## Option 1: Docker Setup (Recommended)

### Step 1: Clone and Configure

```bash
# Navigate to project directory
cd "C:\Users\Mstavo\Desktop\Ai Financial Analytics System"

# Copy environment template
cp .env.example .env
```

### Step 2: Configure Environment

Edit the `.env` file with your settings:

```bash
# Database Configuration
DB_HOST=db
DB_NAME=financial_analytics
DB_USER=postgres
DB_PASSWORD=password
DB_PORT=5432

# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# OpenAI Configuration (Optional - for AI insights)
OPENAI_API_KEY=your-openai-api-key-here

# Frontend Configuration
VITE_API_URL=http://localhost:8000/api
```

**Important**: Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Step 3: Start Services

```bash
# Start all services (database, redis, backend, frontend)
docker-compose up -d

# View logs to monitor startup
docker-compose logs -f
```

### Step 4: Initialize Database

```bash
# Wait for services to be ready, then run migrations
docker-compose exec backend python manage.py migrate

# Create a superuser account
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

### Step 5: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin
- **API Health Check**: http://localhost:8000/api/health/

## Option 2: Manual Setup (Advanced)

### Step 1: Database Setup

```bash
# Start PostgreSQL
sudo service postgresql start  # Linux
# or use your preferred method

# Create database
createdb financial_analytics

# Create user (optional)
createuser financial_analytics_user
```

### Step 2: Redis Setup

```bash
# Start Redis
redis-server
# or use your system's service manager
```

### Step 3: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment and install backend dependencies
./setup_venv.ps1

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Configure environment variables
# Create .env file with same settings as Docker setup
```

If PowerShell blocks script execution, run this once in the current terminal and try again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Step 4: Backend Database Configuration

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 5: Start Backend Services

```bash
# Terminal 1: Start Django server
python manage.py runserver

# Terminal 2: Start Celery worker
celery -A financial_analytics worker --loglevel=info

# Terminal 3: Start Celery beat (for scheduled tasks)
celery -A financial_analytics beat --loglevel=info
```

### Step 6: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment
# Create .env.local with:
VITE_API_URL=http://localhost:8000/api

# Start development server
npm run dev
```

## Testing the System

### 1. Verify Backend is Running

```bash
# Health check
curl http://localhost:8000/api/health/

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-04-26T10:30:00.000Z",
#   "database": "connected",
#   "redis": "connected"
# }
```

### 2. Access Admin Panel

1. Go to http://localhost:8000/admin
2. Login with your superuser credentials
3. You should see the analytics models in the admin interface

### 3. Test Frontend

1. Go to http://localhost:3000
2. You should see the financial analytics dashboard
3. Click "Load Demo Data" to see sample reports

### 4. Test File Upload

1. Navigate to the Upload page
2. Create a sample JSON file (see sample data below)
3. Upload the file and monitor the analysis progress

## Sample Data for Testing

Create a test file `sample_data.json`:

```json
{
  "dashboard": {
    "bank_name": "Sample Bank",
    "period": "Q3 2024",
    "total_assets": 1000000000,
    "total_equity": 100000000,
    "net_income": 12000000,
    "operating_income": 20000000,
    "operating_expenses": 13000000,
    "total_loans": 800000000,
    "total_deposits": 900000000,
    "liquid_assets": 150000000,
    "loan_losses": 8000000,
    "non_performing_loans": 16000000,
    "tier1_capital": 120000000,
    "risk_weighted_assets": 850000000
  },
  "qc_dashboard": {
    "time_series": {
      "total_assets": [950000000, 970000000, 990000000, 1000000000],
      "total_loans": [760000000, 770000000, 785000000, 800000000],
      "total_deposits": [870000000, 880000000, 890000000, 900000000]
    }
  },
  "income_risk": {
    "bank": {
      "roa": 1.2,
      "roe": 12.0,
      "efficiency_ratio": 65.0
    },
    "benchmark": {
      "roa": 0.9,
      "roe": 10.5,
      "efficiency_ratio": 67.8
    }
  },
  "dupont": {
    "components": {
      "profit_margin": 0.6,
      "asset_turnover": 0.8,
      "financial_leverage": 2.5
    }
  }
}
```

## Common Issues and Solutions

### Docker Issues

**Problem: Services won't start**
```bash
# Check logs
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Problem: Database connection errors**
```bash
# Restart database service
docker-compose restart db

# Check database status
docker-compose exec db pg_isready
```

### Backend Issues

**Problem: Migration errors**
```bash
# Reset migrations
docker-compose exec backend python manage.py migrate --fake-initial

# Or reset completely (WARNING: This deletes data)
docker-compose exec backend python manage.py flush
docker-compose exec backend python manage.py migrate
```

**Problem: Celery worker not processing tasks**
```bash
# Check worker status
docker-compose exec celery_worker celery -A financial_analytics inspect active

# Restart worker
docker-compose restart celery_worker
```

### Frontend Issues

**Problem: API connection errors**
```bash
# Check backend is running
curl http://localhost:8000/api/health/

# Check CORS settings in backend settings
# Ensure ALLOWED_HOSTS includes localhost
```

**Problem: Build errors**
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Development Workflow

### 1. Making Changes

**Backend Changes:**
```bash
# Edit code in backend/
# Restart backend service
docker-compose restart backend
```

**Frontend Changes:**
```bash
# Edit code in frontend/src/
# Frontend auto-reloads in development
# For production build:
docker-compose restart frontend
```

### 2. Adding New Features

1. **Backend**: Add models in `analytics/models.py`
2. **API**: Add endpoints in `analytics/views.py`
3. **Frontend**: Add components and views
4. **Tests**: Add tests for new functionality

### 3. Database Changes

```bash
# Create migration
docker-compose exec backend python manage.py makemigrations

# Apply migration
docker-compose exec backend python manage.py migrate
```

## Production Deployment

For production deployment, see the [DEPLOYMENT.md](DEPLOYMENT.md) file for detailed instructions.

## Support

### Getting Help

1. **Check logs**: `docker-compose logs -f [service-name]`
2. **Health checks**: Visit `/api/health/` endpoint
3. **Documentation**: Refer to `DEPLOYMENT.md` for production issues

### Common Commands

```bash
# View all services
docker-compose ps

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend

# Access container shell
docker-compose exec backend bash

# Stop all services
docker-compose down

# Clean up (removes volumes)
docker-compose down -v
```

## Next Steps

Once the system is running:

1. **Explore the Dashboard**: Navigate through different sections
2. **Upload Sample Data**: Test with the provided sample JSON
3. **Generate Reports**: See how AI insights are created
4. **Customize**: Modify prompts, add new metrics, or enhance the UI
5. **Deploy**: Follow DEPLOYMENT.md for production setup

The system is now ready for financial data analysis and report generation!
