# Deployment Guide

This document provides comprehensive instructions for deploying the AI Financial Analytics System in various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Production Configuration](#production-configuration)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended) or macOS
- **Memory**: Minimum 4GB RAM, 8GB+ recommended
- **Storage**: Minimum 20GB available space
- **CPU**: 2+ cores recommended

### Software Dependencies

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Nginx (for production)

## Environment Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-financial-analytics-system
```

### 2. Environment Configuration

Copy the environment template and configure:

```bash
cp .env.example .env
```

Edit `.env` with your specific values:

```bash
# Database Configuration
DB_HOST=localhost
DB_NAME=financial_analytics
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_PORT=5432

# Django Configuration
DEBUG=False
SECRET_KEY=your-very-secure-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Frontend Configuration
VITE_API_URL=https://your-domain.com/api
```

### 3. Generate Django Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Use the output as your `SECRET_KEY`.

## Docker Deployment (Recommended)

### 1. Build and Start Services

```bash
# Start all services
docker-compose up -d

# Build images (first time or after changes)
docker-compose build

# View logs
docker-compose logs -f
```

### 2. Initialize Database

```bash
# Run database migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

### 3. Verify Deployment

Check service status:

```bash
docker-compose ps
```

Test API endpoints:

```bash
curl http://localhost:8000/api/health/
```

### 4. Production Services

For production, exclude the development frontend:

```bash
docker-compose --profile production up -d
```

## Manual Deployment

### Backend Setup

1. **Install Python Dependencies**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Database Setup**

```bash
# Create database
createdb financial_analytics

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

3. **Start Services**

```bash
# Start Django server
gunicorn --bind 0.0.0.0:8000 --workers 4 financial_analytics.wsgi:application

# Start Celery worker (separate terminal)
celery -A financial_analytics worker --loglevel=info

# Start Celery beat (separate terminal)
celery -A financial_analytics beat --loglevel=info
```

### Frontend Setup

1. **Install Dependencies**

```bash
cd frontend
npm install
```

2. **Build for Production**

```bash
npm run build
```

3. **Serve with Nginx**

Create `/etc/nginx/sites-available/financial-analytics`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /path/to/backend/staticfiles/;
    }

    # Media files
    location /media/ {
        alias /path/to/backend/media/;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/financial-analytics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Production Configuration

### Security Settings

1. **Django Settings**

```python
# production.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

2. **Database Security**

```bash
# Create dedicated database user
sudo -u postgres createuser --interactive financial_analytics_user
sudo -u postgres createdb -O financial_analytics_user financial_analytics_db
```

3. **Firewall Configuration**

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow SSH (if needed)
sudo ufw allow 22

# Enable firewall
sudo ufw enable
```

### SSL/TLS Setup

1. **Let's Encrypt Certificate**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

2. **Auto-renewal**

```bash
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Performance Optimization

1. **Database Optimization**

```sql
-- PostgreSQL configuration
-- Add to postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

2. **Redis Configuration**

```bash
# /etc/redis/redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

3. **Nginx Optimization**

```nginx
# Add to server block
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

# Caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Monitoring and Maintenance

### Health Checks

1. **Application Health**

```bash
# API health check
curl -f http://localhost:8000/api/health/

# Database connection
docker-compose exec backend python manage.py dbshell --command "SELECT 1;"
```

2. **Service Monitoring**

Create `monitor.sh`:

```bash
#!/bin/bash

# Check if services are running
services=("db" "redis" "backend" "celery_worker" "celery_beat")

for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        echo "✓ $service is running"
    else
        echo "✗ $service is down"
    fi
done
```

### Log Management

1. **Log Rotation**

Create `/etc/logrotate.d/financial-analytics`:

```
/path/to/backend/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        docker-compose restart backend
    endscript
}
```

2. **Centralized Logging**

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### Backup Strategy

1. **Database Backup**

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/financial-analytics"

docker-compose exec -T db pg_dump -U postgres financial_analytics > "$BACKUP_DIR/db_backup_$DATE.sql"

# Keep last 30 days
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +30 -delete
```

2. **Media Backup**

```bash
#!/bin/bash
# backup_media.sh
rsync -av /path/to/backend/media/ /backups/financial-analytics/media/
```

### Scaling Considerations

1. **Horizontal Scaling**

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3
  
  celery_worker:
    deploy:
      replicas: 2
```

2. **Load Balancing**

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**

```bash
# Check database status
docker-compose exec db pg_isready

# Check logs
docker-compose logs db
```

2. **Celery Task Issues**

```bash
# Check worker status
docker-compose exec celery_worker celery -A financial_analytics inspect active

# Clear queue
docker-compose exec celery_worker celery -A financial_analytics purge
```

3. **Frontend Build Issues**

```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Performance Issues

1. **Slow API Responses**

```bash
# Database queries
docker-compose exec backend python manage.py dbshell --command "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Memory usage
docker stats
```

2. **High Memory Usage**

```bash
# Check process memory
docker-compose exec backend ps aux

# Restart services
docker-compose restart backend celery_worker
```

## Maintenance Tasks

### Regular Maintenance

1. **Daily Tasks**

```bash
# Health check
./monitor.sh

# Log cleanup
find /var/log -name "*.log" -mtime +7 -delete
```

2. **Weekly Tasks**

```bash
# Database maintenance
docker-compose exec backend python manage.py dbshell --command "VACUUM ANALYZE;"

# Update dependencies
cd backend && pip install -r requirements.txt --upgrade
cd frontend && npm update
```

3. **Monthly Tasks**

```bash
# Security updates
sudo apt update && sudo apt upgrade

# Certificate renewal check
sudo certbot renew --dry-run
```

### Emergency Procedures

1. **Service Recovery**

```bash
# Restart all services
docker-compose restart

# Full rebuild
docker-compose down
docker-compose up -d --build
```

2. **Data Recovery**

```bash
# Restore database
docker-compose exec -T db psql -U postgres financial_analytics < backup.sql
```

This deployment guide provides comprehensive instructions for deploying and maintaining the AI Financial Analytics System in production environments.
