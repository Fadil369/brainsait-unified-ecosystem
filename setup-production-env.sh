#!/bin/bash

# BrainSAIT Healthcare Platform - Production Environment Setup
# Generates secure environment variables for production deployment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== BrainSAIT Healthcare Platform - Production Environment Setup ===${NC}"
echo ""

# Function to generate secure password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Function to generate JWT secret
generate_jwt_secret() {
    openssl rand -base64 64 | tr -d "\n"
}

# Function to get user input with default
get_input() {
    local prompt="$1"
    local default="$2"
    local result

    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " result
        echo "${result:-$default}"
    else
        read -p "$prompt: " result
        echo "$result"
    fi
}

echo -e "${GREEN}Generating secure environment configuration...${NC}"
echo ""

# Get domain information
DOMAIN=$(get_input "Enter your domain name" "your-domain.com")
EMAIL=$(get_input "Enter your email for SSL certificates" "admin@${DOMAIN}")

# Generate secure passwords
DB_PASSWORD=$(generate_password)
REDIS_PASSWORD=$(generate_password)
JWT_SECRET=$(generate_jwt_secret)
ENCRYPTION_KEY=$(generate_password)

# Get NPHIES credentials (optional)
echo ""
echo -e "${YELLOW}NPHIES Integration (Saudi Healthcare):${NC}"
NPHIES_CLIENT_ID=$(get_input "Enter NPHIES Client ID (optional)" "")
NPHIES_CLIENT_SECRET=$(get_input "Enter NPHIES Client Secret (optional)" "")

# Create production environment file
cat > .env.production << EOF
# BrainSAIT Healthcare Platform - Production Environment
# Generated on $(date)

# =================
# Database Configuration
# =================
DB_HOST=postgres
DB_PORT=5432
DB_NAME=brainsait_healthcare
DB_USER=brainsait_admin
DB_PASSWORD=${DB_PASSWORD}

# =================
# Redis Configuration
# =================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD}

# =================
# Security Configuration
# =================
JWT_SECRET_KEY=${JWT_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# =================
# Healthcare Compliance
# =================
PDPL_COMPLIANCE=true
HIPAA_COMPLIANCE=true
AUDIT_LOGGING=true
SECURITY_HEADERS=true
CSRF_PROTECTION=true

# =================
# Arabic RTL Support
# =================
ARABIC_SUPPORT=true
RTL_ENABLED=true
LANGUAGE_DEFAULT=ar

# =================
# NPHIES Integration (Saudi Healthcare)
# =================
NPHIES_CLIENT_ID=${NPHIES_CLIENT_ID}
NPHIES_CLIENT_SECRET=${NPHIES_CLIENT_SECRET}
NPHIES_BASE_URL=https://api.nphies.sa
NPHIES_ENVIRONMENT=production

# =================
# API Configuration
# =================
API_BASE_URL=https://${DOMAIN}/api
FRONTEND_URL=https://${DOMAIN}
BACKEND_PORT=8000
FRONTEND_PORT=3000

# =================
# SSL and Domain Configuration
# =================
DOMAIN=${DOMAIN}
SSL_EMAIL=${EMAIL}
ENABLE_HTTPS=true

# =================
# Application Settings
# =================
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE=10485760
SESSION_TIMEOUT=3600

# =================
# Performance Configuration
# =================
WORKERS=2
MAX_CONNECTIONS=100
CONNECTION_TIMEOUT=30
REQUEST_TIMEOUT=30

# =================
# Backup Configuration
# =================
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=30

# =================
# Monitoring and Alerts
# =================
HEALTH_CHECK_ENABLED=true
METRICS_ENABLED=true
ALERTS_EMAIL=${EMAIL}

# =================
# Coolify Integration
# =================
COOLIFY_PROJECT=brainsait-healthcare
COOLIFY_STACK=healthcare-platform

# =================
# CORS Configuration
# =================
CORS_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=Content-Type,Authorization,X-CSRF-Token

# =================
# Rate Limiting
# =================
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=100

# =================
# File Storage
# =================
UPLOAD_PATH=/app/uploads
STATIC_PATH=/app/static
TEMP_PATH=/tmp
EOF

echo ""
echo -e "${GREEN}✅ Production environment file created: .env.production${NC}"
echo ""
echo -e "${YELLOW}📋 Generated Credentials (SAVE THESE SECURELY):${NC}"
echo "Domain: ${DOMAIN}"
echo "Database Password: ${DB_PASSWORD}"
echo "Redis Password: ${REDIS_PASSWORD}"
echo "JWT Secret: ${JWT_SECRET:0:20}..."
echo "Encryption Key: ${ENCRYPTION_KEY}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "1. Review and update .env.production if needed"
echo "2. Run: ./deploy-to-vps-prod.sh"
echo "3. Configure your domain DNS to point to your VPS IP"
echo "4. Access your application at https://${DOMAIN}"
echo ""
echo -e "${YELLOW}⚠️  Important Security Notes:${NC}"
echo "- Keep the .env.production file secure and private"
echo "- Use these credentials only for production deployment"
echo "- Enable SSL certificates after deployment"
echo "- Set up regular database backups"
echo ""
