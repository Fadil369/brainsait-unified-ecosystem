# 🚀 BrainSAIT Healthcare Platform - VPS Deployment Guide

## Overview

This comprehensive guide covers the deployment of the BrainSAIT Unified Healthcare Platform on Virtual Private Servers (VPS), providing secure, scalable, and compliant healthcare infrastructure for Saudi Arabia's healthcare sector.

## 🏗️ Infrastructure Requirements

### Minimum VPS Specifications

#### Production Environment
- **CPU**: 8 vCPUs (Intel Xeon or AMD EPYC)
- **RAM**: 32 GB DDR4
- **Storage**: 500 GB NVMe SSD
- **Network**: 1 Gbps connection
- **OS**: Ubuntu 22.04 LTS or CentOS 8+

#### Development Environment
- **CPU**: 4 vCPUs
- **RAM**: 16 GB
- **Storage**: 200 GB SSD
- **Network**: 500 Mbps connection
- **OS**: Ubuntu 22.04 LTS

### Recommended VPS Providers
- **Saudi Arabia**: Saudi Telecom Company (STC), Mobily Cloud
- **Regional**: AWS Middle East (Bahrain), Azure UAE
- **International**: DigitalOcean, Linode, Vultr (with data residency compliance)

## 🔧 Pre-Deployment Setup

### 1. Server Preparation
```bash
#!/bin/bash
# Initial server setup script

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git unzip htop

# Configure firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp

# Set up fail2ban for security
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 2. Docker Installation
```bash
#!/bin/bash
# Docker installation script

# Remove old Docker versions
sudo apt remove -y docker docker-engine docker.io containerd runc

# Install Docker dependencies
sudo apt install -y apt-transport-https ca-certificates gnupg lsb-release

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Configure Docker for non-root user
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. SSL Certificate Setup
```bash
#!/bin/bash
# SSL certificate installation with Let's Encrypt

# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Generate SSL certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Set up automatic renewal
sudo crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -
```

## 📦 Application Deployment

### 1. Clone and Setup Repository
```bash
#!/bin/bash
# Application deployment script

# Clone the repository
git clone https://github.com/Fadil369/brainsait-unified-ecosystem.git
cd brainsait-unified-ecosystem

# Create production environment file
cp .env.production.template .env.production

# Configure production environment
nano .env.production
```

### 2. Production Environment Configuration
```bash
# .env.production configuration
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=brainsait_healthcare_prod
DB_USER=brainsait_admin
DB_PASSWORD=your_secure_password_here

# Security Configuration
JWT_SECRET_KEY=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here
MFA_SECRET=your_mfa_secret_here

# NPHIES Configuration
NPHIES_CLIENT_ID=your_nphies_client_id
NPHIES_CLIENT_SECRET=your_nphies_client_secret
NPHIES_API_URL=https://api.nphies.sa

# Twilio Configuration (HIPAA Compliant)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@domain.com
SMTP_PASSWORD=your_email_password

# Production Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

### 3. Docker Compose Production Deployment
```yaml
# docker-compose.production.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: brainsait_healthcare_prod
      POSTGRES_USER: brainsait_admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DB_HOST=postgres
      - REDIS_HOST=redis
    volumes:
      - ./backend:/app
      - logs:/app/logs
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  frontend:
    build:
      context: ./oid-portal
      dockerfile: Dockerfile.prod
    volumes:
      - ./oid-portal/dist:/usr/share/nginx/html
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - logs:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  logs:
```

## 🔒 Security Hardening

### 1. System Security Configuration
```bash
#!/bin/bash
# System security hardening script

# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Change default SSH port
sudo sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config

# Disable password authentication
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Restart SSH service
sudo systemctl restart sshd

# Install and configure automated security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 2. Nginx Security Configuration
```nginx
# /etc/nginx/sites-available/brainsait-healthcare
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## 📊 Monitoring and Logging

### 1. Application Monitoring Setup
```bash
#!/bin/bash
# Monitoring stack installation

# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/latest/download/prometheus-*.linux-amd64.tar.gz
tar -xzf prometheus-*.linux-amd64.tar.gz
sudo mv prometheus-*/prometheus /usr/local/bin/
sudo mv prometheus-*/promtool /usr/local/bin/

# Install Grafana
sudo apt-get install -y apt-transport-https
sudo apt-get install -y software-properties-common wget
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install grafana

# Start services
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

### 2. Log Management Configuration
```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash/config:/usr/share/logstash/config
      - logs:/logs
    ports:
      - "5044:5044"
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
  logs:
```

## 🔄 Backup and Recovery

### 1. Database Backup Script
```bash
#!/bin/bash
# Database backup script

BACKUP_DIR="/var/backups/brainsait"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="brainsait_healthcare_prod"

# Create backup directory
mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_dump -h localhost -U brainsait_admin $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Upload to cloud storage (optional)
# aws s3 cp $BACKUP_DIR/db_backup_$DATE.sql.gz s3://your-backup-bucket/

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### 2. Automated Backup Cron Job
```bash
# Add to crontab: crontab -e
# Daily backup at 2 AM
0 2 * * * /opt/brainsait/backup.sh >> /var/log/backup.log 2>&1

# Weekly full system backup
0 3 * * 0 /opt/brainsait/full_backup.sh >> /var/log/full_backup.log 2>&1
```

## 🚀 Deployment Script

### Complete Deployment Automation
```bash
#!/bin/bash
# deploy-production.sh - Complete deployment automation

set -e

echo "🚀 Starting BrainSAIT Healthcare Platform deployment..."

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
sudo mkdir -p /opt/brainsait/{logs,backups,ssl}

# Set permissions
sudo chown -R $USER:$USER /opt/brainsait

# Copy SSL certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/* /opt/brainsait/ssl/

# Build and deploy
echo "📦 Building application containers..."
docker-compose -f docker-compose.production.yml build

echo "🔧 Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head

# Setup backup cron job
echo "💾 Setting up automated backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/brainsait/backup.sh") | crontab -

# Configure monitoring
echo "📊 Setting up monitoring..."
docker-compose -f docker-compose.logging.yml up -d

# Health check
echo "🏥 Performing health check..."
if curl -f http://localhost:8000/health; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    exit 1
fi

if curl -f http://localhost:3000; then
    echo "✅ Frontend health check passed"
else
    echo "❌ Frontend health check failed"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo "🌐 Your application is available at: https://yourdomain.com"
echo "📊 Monitoring dashboard: http://yourdomain.com:5601"
echo "📈 Metrics dashboard: http://yourdomain.com:3000"
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### Docker Issues
```bash
# Container won't start
docker-compose logs service_name

# Out of disk space
docker system prune -a

# Permission denied
sudo chown -R $USER:$USER /var/lib/docker
```

#### Database Issues
```bash
# Connection refused
docker-compose exec postgres pg_isready

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### SSL Issues
```bash
# Certificate renewal
sudo certbot renew --dry-run

# Check certificate status
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -text -noout
```

## 📞 Support and Maintenance

### Maintenance Schedule
- **Daily**: Automated backups and log rotation
- **Weekly**: Security updates and system monitoring review
- **Monthly**: Full system backup and disaster recovery testing
- **Quarterly**: Performance optimization and capacity planning

### Support Contacts
- **Technical Support**: support@brainsait.com
- **Emergency**: +966-XX-XXX-XXXX
- **Documentation**: https://docs.brainsait.com

---

**Last Updated**: November 2024  
**Version**: 2.0.0  
**Tested On**: Ubuntu 22.04 LTS, CentOS 8+

*This deployment guide ensures secure, scalable, and compliant deployment of the BrainSAIT Healthcare Platform in production environments.*
