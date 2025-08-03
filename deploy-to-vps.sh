#!/bin/bash

# BrainSAIT OID System Deployment Script for VPS
set -e

echo "🚀 Starting BrainSAIT OID System deployment to VPS..."

# Configuration
VPS_HOST="82.25.101.65"
VPS_USER="root"
PROJECT_NAME="brainsait-oid-system"
LOCAL_PROJECT_PATH="/Users/fadil369/02_BRAINSAIT_ECOSYSTEM/Unified_Platform/UNIFICATION_SYSTEM/brainSAIT-oid-system"
REMOTE_PROJECT_PATH="/opt/$PROJECT_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if we can connect to VPS
check_vps_connection() {
    print_status "Checking VPS connection..."
    if ssh -o ConnectTimeout=10 -o BatchMode=yes $VPS_USER@$VPS_HOST exit 2>/dev/null; then
        print_status "✅ VPS connection successful"
        return 0
    else
        print_error "❌ Cannot connect to VPS. Please check your SSH connection."
        return 1
    fi
}

# Function to prepare local files
prepare_local_files() {
    print_status "Preparing local files for deployment..."
    
    # Create deployment directory
    mkdir -p ./deployment
    
    # Copy necessary files
    cp docker-compose.yml ./deployment/docker-compose.yml
    cp .env.production ./deployment/.env
    
    # Create deployment package
    tar -czf deployment/brainsait-deployment.tar.gz \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='.DS_Store' \
        --exclude='deployment' \
        .
    
    print_status "✅ Local files prepared"
}

# Function to setup VPS environment
setup_vps_environment() {
    print_status "Setting up VPS environment..."
    
    ssh $VPS_USER@$VPS_HOST << 'EOF'
        # Update system
        apt-get update -y
        
        # Install required packages if not present
        which docker >/dev/null 2>&1 || {
            echo "Installing Docker..."
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
        }
        
        which docker-compose >/dev/null 2>&1 || {
            echo "Installing Docker Compose..."
            curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            chmod +x /usr/local/bin/docker-compose
        }
        
        # Create project directory
        mkdir -p /opt/brainsait-oid-system
        cd /opt/brainsait-oid-system
        
        # Ensure Docker is running
        systemctl start docker
        systemctl enable docker
        
        echo "VPS environment setup completed"
EOF
    
    print_status "✅ VPS environment ready"
}

# Function to deploy application
deploy_application() {
    print_status "Deploying application to VPS..."
    
    # Upload deployment package
    scp deployment/brainsait-deployment.tar.gz $VPS_USER@$VPS_HOST:$REMOTE_PROJECT_PATH/
    
    # Deploy on VPS
    ssh $VPS_USER@$VPS_HOST << EOF
        cd $REMOTE_PROJECT_PATH
        
        # Stop existing containers if running
        if [ -f docker-compose.yml ]; then
            docker-compose down 2>/dev/null || true
        fi
        
        # Extract new deployment
        tar -xzf brainsait-deployment.tar.gz
        rm brainsait-deployment.tar.gz
        
        # Set proper permissions
        chmod +x setup_github.sh test.sh
        
        # Start services
        docker-compose up -d --build
        
        # Wait for services to start
        sleep 30
        
        # Check if services are running
        docker-compose ps
        
        echo "Deployment completed!"
EOF
    
    print_status "✅ Application deployed"
}

# Function to verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Test backend
    if curl -f http://$VPS_HOST:8000/health 2>/dev/null; then
        print_status "✅ Backend is responding"
    else
        print_warning "⚠️  Backend health check failed - checking logs..."
        ssh $VPS_USER@$VPS_HOST "cd $REMOTE_PROJECT_PATH && docker-compose logs backend"
    fi
    
    # Test frontend
    if curl -f http://$VPS_HOST:3000 2>/dev/null; then
        print_status "✅ Frontend is responding"
    else
        print_warning "⚠️  Frontend check failed - checking logs..."
        ssh $VPS_USER@$VPS_HOST "cd $REMOTE_PROJECT_PATH && docker-compose logs frontend"
    fi
}

# Function to show deployment info
show_deployment_info() {
    print_status "Deployment Information:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🌐 Frontend URL: http://$VPS_HOST:3000"
    echo "🔧 Backend API: http://$VPS_HOST:8000"
    echo "📊 API Docs: http://$VPS_HOST:8000/docs"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    print_status "To monitor your application:"
    echo "ssh $VPS_USER@$VPS_HOST 'cd $REMOTE_PROJECT_PATH && docker-compose logs -f'"
    echo ""
    print_status "To stop your application:"
    echo "ssh $VPS_USER@$VPS_HOST 'cd $REMOTE_PROJECT_PATH && docker-compose down'"
    echo ""
    print_status "To restart your application:"
    echo "ssh $VPS_USER@$VPS_HOST 'cd $REMOTE_PROJECT_PATH && docker-compose restart'"
}

# Main deployment process
main() {
    print_status "🏥 BrainSAIT OID System - VPS Deployment"
    print_status "========================================"
    
    # Check prerequisites
    if ! command -v ssh &> /dev/null; then
        print_error "SSH is required but not installed."
        exit 1
    fi
    
    if ! command -v scp &> /dev/null; then
        print_error "SCP is required but not installed."
        exit 1
    fi
    
    # Execute deployment steps
    check_vps_connection || exit 1
    prepare_local_files
    setup_vps_environment
    deploy_application
    
    print_status "Waiting for services to stabilize..."
    sleep 20
    
    verify_deployment
    show_deployment_info
    
    print_status "🎉 Deployment completed successfully!"
}

# Run main function
main "$@"
