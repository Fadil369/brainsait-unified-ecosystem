#!/bin/bash

# BrainSAIT Healthcare Platform - Quick Start Script
# This script handles Python version compatibility and starts the development environment

set -e  # Exit on any error

echo "🚀 Starting BrainSAIT Healthcare Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the correct directory
if [[ ! -f "docker-compose.yml" ]]; then
    print_error "docker-compose.yml not found. Please run this script from the project root directory."
    exit 1
fi

# Function to check if compatible Python is available
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
        print_success "Found Python 3.11: $PYTHON_CMD"
        return 0
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [[ "$PYTHON_MAJOR" == "3" ]] && [[ "$PYTHON_MINOR" -ge 11 ]]; then
            PYTHON_CMD="python3"
            print_success "Found compatible Python $PYTHON_VERSION: $PYTHON_CMD"
            return 0
        else
            print_warning "Python $PYTHON_VERSION found, but requires 3.11+. Using Docker instead."
            return 1
        fi
    else
        print_warning "Python 3 not found. Using Docker instead."
        return 1
    fi
}

# Function to setup Python virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    cd backend
    
    if [[ ! -d "venv" ]]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    
    # Try different requirements files based on what's available
    if [[ -f "requirements-minimal.txt" ]]; then
        print_status "Using minimal requirements for compatibility..."
        pip install -r requirements-minimal.txt
    elif [[ -f "requirements-python311.txt" ]]; then
        print_status "Using Python 3.11+ compatible requirements..."
        pip install -r requirements-python311.txt
    elif [[ -f "requirements.txt" ]]; then
        print_status "Using standard requirements..."
        pip install -r requirements.txt
    else
        print_error "No requirements file found!"
        return 1
    fi
    
    cd ..
    print_success "Python environment ready"
}

# Function to check Node.js and npm
check_node() {
    print_status "Checking Node.js and npm..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found. Please install Node.js 18+ to run the frontend."
        return 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm not found. Please install npm to run the frontend."
        return 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [[ "$NODE_VERSION" -lt 18 ]]; then
        print_warning "Node.js version is $NODE_VERSION. Recommended version is 18+."
    fi
    
    print_success "Node.js $(node --version) and npm $(npm --version) found"
    return 0
}

# Function to setup frontend dependencies
setup_frontend() {
    print_status "Setting up frontend dependencies..."
    
    cd oid-portal
    
    if [[ ! -d "node_modules" ]]; then
        print_status "Installing npm dependencies..."
        npm install
    else
        print_status "npm dependencies already installed"
    fi
    
    cd ..
    print_success "Frontend dependencies ready"
}

# Function to start with Docker
start_with_docker() {
    print_status "Starting with Docker..."
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    print_status "Building and starting containers..."
    docker-compose down --remove-orphans
    docker-compose up --build -d
    
    print_status "Waiting for services to start..."
    sleep 10
    
    # Check backend health
    print_status "Checking backend health..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            print_success "Backend is healthy!"
            break
        fi
        if [[ $i -eq 30 ]]; then
            print_error "Backend failed to start properly"
            docker-compose logs backend
            exit 1
        fi
        sleep 2
    done
    
    print_success "BrainSAIT Healthcare Platform started with Docker!"
    print_status "Backend API: http://localhost:8000"
    print_status "Frontend: http://localhost:5173"
    print_status "Database: localhost:5432"
    print_status "API Documentation: http://localhost:8000/docs"
    
    echo ""
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop: docker-compose down"
}

# Function to start with local Python
start_with_python() {
    print_status "Starting with local Python..."
    
    # Start database with Docker
    print_status "Starting PostgreSQL database..."
    docker-compose up -d db
    
    # Wait for database
    print_status "Waiting for database to be ready..."
    for i in {1..30}; do
        if docker-compose exec -T db pg_isready -U oid_admin -d oid_registry &> /dev/null; then
            print_success "Database is ready!"
            break
        fi
        if [[ $i -eq 30 ]]; then
            print_error "Database failed to start"
            exit 1
        fi
        sleep 2
    done
    
    # Start backend
    print_status "Starting backend server..."
    cd backend
    source venv/bin/activate
    
    # Use the simple main file that doesn't require problematic dependencies
    if [[ -f "main_simple.py" ]]; then
        python main_simple.py &
    else
        python main.py &
    fi
    
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            print_success "Backend is healthy!"
            break
        fi
        if [[ $i -eq 30 ]]; then
            print_error "Backend failed to start"
            kill $BACKEND_PID 2>/dev/null || true
            exit 1
        fi
        sleep 2
    done
    
    # Start frontend
    print_status "Starting frontend development server..."
    cd oid-portal
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    print_success "BrainSAIT Healthcare Platform started!"
    print_status "Backend API: http://localhost:8000"
    print_status "Frontend: http://localhost:5173"
    print_status "Database: localhost:5432"
    print_status "API Documentation: http://localhost:8000/docs"
    
    echo ""
    print_status "Press Ctrl+C to stop all services"
    
    # Trap Ctrl+C to clean up processes
    trap 'print_status "Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; docker-compose down; exit 0' INT
    
    # Wait for processes
    wait
}

# Function to show help
show_help() {
    echo "BrainSAIT Healthcare Platform - Quick Start Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --docker       Force Docker mode"
    echo "  --python       Force Python mode (requires Python 3.11)"
    echo "  --help         Show this help message"
    echo ""
    echo "Default behavior:"
    echo "  - Try Python 3.11 first"
    echo "  - Fall back to Docker if Python 3.11 not available"
}

# Parse command line arguments
FORCE_DOCKER=false
FORCE_PYTHON=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --docker)
            FORCE_DOCKER=true
            shift
            ;;
        --python)
            FORCE_PYTHON=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution logic
print_status "BrainSAIT Healthcare Platform Startup"
print_status "======================================"

if [[ "$FORCE_DOCKER" == "true" ]]; then
    print_status "Docker mode forced"
    start_with_docker
elif [[ "$FORCE_PYTHON" == "true" ]]; then
    print_status "Python mode forced"
    if check_python && check_node; then
        setup_venv
        setup_frontend
        start_with_python
    else
        print_error "Python 3.11 or Node.js requirements not met"
        exit 1
    fi
else
    # Auto-detect best mode
    if check_python && check_node; then
        print_status "Using Python mode (Python 3.11 + Node.js detected)"
        setup_venv
        setup_frontend
        start_with_python
    else
        print_status "Using Docker mode (Python 3.11 or Node.js not available)"
        start_with_docker
    fi
fi