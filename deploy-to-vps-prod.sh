#!/bin/bash

# BrainSAIT Healthcare Platform - VPS Deployment Script
# Optimized for production deployment with Arabic RTL support and healthcare compliance

set -e

# Configuration
VPS_HOST="82.25.101.65"
VPS_USER="root"
PROJECT_NAME="brainsait-healthcare"
DOMAIN="coolify.thefadil.site"  # Updated with your domain
EMAIL="dr.mf.122986@icloud.com"  # Updated with your email

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    if ! command -v ssh &> /dev/null; then
        error "SSH client not found. Please install SSH."
        exit 1
    fi

    if ! command -v scp &> /dev/null; then
        error "SCP not found. Please install SCP."
        exit 1
    fi

    info "Prerequisites check passed."
}

# Test SSH connection
test_ssh_connection() {
    log "Testing SSH connection to ${VPS_HOST}..."

    if ssh -o ConnectTimeout=10 -o BatchMode=yes ${VPS_USER}@${VPS_HOST} exit; then
        info "SSH connection successful."
    else
        error "Cannot connect to VPS. Please check:"
        echo "  1. VPS is running and accessible"
        echo "  2. SSH key is properly configured"
        echo "  3. IP address is correct: ${VPS_HOST}"
        exit 1
    fi
}

# Prepare deployment files
prepare_deployment() {
    log "Preparing deployment files..."

    # Create deployment directory
    mkdir -p deployment

    # Copy necessary files
    cp docker-compose.coolify.yml deployment/
    cp -r backend deployment/
    cp -r oid-portal deployment/
    cp -r nginx deployment/

    # Create environment file for production
    cat > deployment/.env << EOF
# Production Environment Configuration
ENVIRONMENT=production

# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=brainsait_healthcare
DB_USER=brainsait_admin
DB_PASSWORD=\${DB_PASSWORD}

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=\${REDIS_PASSWORD}

# Security Configuration
JWT_SECRET_KEY=\${JWT_SECRET_KEY}
ENCRYPTION_KEY=\${ENCRYPTION_KEY}

# Healthcare Compliance
PDPL_COMPLIANCE=true
HIPAA_COMPLIANCE=true
AUDIT_LOGGING=true

# Arabic RTL Support
ARABIC_SUPPORT=true
RTL_ENABLED=true

# NPHIES Integration
NPHIES_CLIENT_ID=\${NPHIES_CLIENT_ID}
NPHIES_CLIENT_SECRET=\${NPHIES_CLIENT_SECRET}
NPHIES_BASE_URL=https://api.nphies.sa

# API Configuration
API_BASE_URL=https://${DOMAIN}/api
FRONTEND_URL=https://${DOMAIN}

# Coolify Configuration
COOLIFY_PROJECT=${PROJECT_NAME}
COOLIFY_DOMAIN=${DOMAIN}

# SSL Configuration
SSL_EMAIL=${EMAIL}
EOF

    info "Deployment files prepared."
}

# Upload files to VPS
upload_files() {
    log "Uploading files to VPS..."

    # Create project directory on VPS
    ssh ${VPS_USER}@${VPS_HOST} "mkdir -p /opt/${PROJECT_NAME}"

    # Upload deployment files
    scp -r deployment/* ${VPS_USER}@${VPS_HOST}:/opt/${PROJECT_NAME}/

    info "Files uploaded successfully."
}

# Setup VPS environment
setup_vps_environment() {
    log "Setting up VPS environment..."

    ssh ${VPS_USER}@${VPS_HOST} << 'EOF'
# Update system packages
apt-get update
apt-get upgrade -y

# Install required packages
apt-get install -y curl wget git nano htop

# Ensure Docker is running
systemctl enable docker
systemctl start docker

# Ensure Coolify is running
systemctl enable coolify
systemctl start coolify

# Create backup directory
mkdir -p /opt/backup

# Set proper permissions
chmod -R 755 /opt/brainsait-healthcare
EOF

    info "VPS environment setup completed."
}

# Deploy with Coolify
deploy_with_coolify() {
    log "Deploying with Coolify..."

    ssh ${VPS_USER}@${VPS_HOST} << EOF
cd /opt/${PROJECT_NAME}

# Stop existing containers if any
docker-compose -f docker-compose.coolify.yml down || true

# Pull latest images and deploy
docker-compose -f docker-compose.coolify.yml pull
docker-compose -f docker-compose.coolify.yml up -d

# Wait for services to start
sleep 30

# Check service status
docker-compose -f docker-compose.coolify.yml ps
EOF

    info "Deployment completed."
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."

    # Check if services are running
    ssh ${VPS_USER}@${VPS_HOST} << EOF
cd /opt/${PROJECT_NAME}

echo "=== Container Status ==="
docker-compose -f docker-compose.coolify.yml ps

echo "=== Backend Health Check ==="
curl -f http://localhost:8000/health || echo "Backend health check failed"

echo "=== Frontend Health Check ==="
curl -f http://localhost:3000 || echo "Frontend health check failed"

echo "=== Database Connection ==="
docker-compose -f docker-compose.coolify.yml exec -T postgres pg_isready -U brainsait_admin || echo "Database connection failed"
EOF

    info "Deployment verification completed."
}

# Setup SSL with Let's Encrypt
setup_ssl() {
    log "Setting up SSL with Let's Encrypt..."

    ssh ${VPS_USER}@${VPS_HOST} << EOF
# Install certbot if not already installed
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d ${DOMAIN} --email ${EMAIL} --agree-tos --non-interactive

# Setup auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer
EOF

    info "SSL setup completed."
}

# Cleanup local deployment files
cleanup() {
    log "Cleaning up local deployment files..."
    rm -rf deployment
    info "Cleanup completed."
}

# Main deployment function
main() {
    log "Starting BrainSAIT Healthcare Platform deployment to VPS..."

    check_prerequisites
    test_ssh_connection
    prepare_deployment
    upload_files
    setup_vps_environment
    deploy_with_coolify
    verify_deployment

    if [ "$1" = "--ssl" ]; then
        setup_ssl
    fi

    cleanup

    log "Deployment completed successfully!"
    echo ""
    info "Your BrainSAIT Healthcare Platform is now deployed at:"
    echo "  Frontend: https://${DOMAIN}"
    echo "  Backend API: https://${DOMAIN}/api"
    echo ""
    warning "Don't forget to:"
    echo "  1. Update your domain DNS to point to ${VPS_HOST}"
    echo "  2. Configure environment variables in Coolify dashboard"
    echo "  3. Set up database backups"
    echo "  4. Configure monitoring and alerts"
}

# Run main function with all arguments
main "$@"
