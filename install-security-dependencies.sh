#!/bin/bash

# BrainSAIT Healthcare Platform - Security Dependencies Installation Script
# Version: 2.0.0
# Purpose: Install and configure security tools and dependencies for healthcare compliance

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/security-install.log"
ENVIRONMENT="${ENVIRONMENT:-development}"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "$timestamp [$level] $message" | tee -a "$LOG_FILE"
}

# Display banner
show_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                    ║"
    echo "║           🔐 BrainSAIT Security Dependencies Installer 🔐         ║"
    echo "║                                                                    ║"
    echo "║      HIPAA Compliance • PDPL Compliance • Healthcare Security     ║"
    echo "║                                                                    ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
}

# Check if running as root
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        echo -e "${RED}❌ This script should not be run as root for security reasons${NC}"
        echo "Please run as a regular user with sudo privileges"
        exit 1
    fi
    
    if ! sudo -n true 2>/dev/null; then
        echo -e "${YELLOW}⚠ This script requires sudo privileges${NC}"
        echo "Please ensure you can run sudo commands"
    fi
}

# System security tools installation
install_system_security() {
    log "INFO" "Installing system security tools..."
    
    echo -e "${BLUE}🔧 Installing system security packages...${NC}"
    
    # Update package manager
    sudo apt update
    
    # Essential security tools
    local security_packages=(
        "fail2ban"           # Intrusion prevention
        "ufw"                # Uncomplicated firewall
        "rkhunter"           # Rootkit hunter
        "chkrootkit"         # Rootkit checker
        "clamav"             # Antivirus
        "clamav-daemon"      # Antivirus daemon
        "auditd"             # Audit daemon
        "aide"               # Advanced intrusion detection
        "lynis"              # Security auditing tool
        "unattended-upgrades" # Automatic security updates
        "apt-listchanges"    # Package change notifications
        "needrestart"        # Service restart notifications
    )
    
    for package in "${security_packages[@]}"; do
        if dpkg -l | grep -q "^ii  $package "; then
            echo -e "${GREEN}✓${NC} $package already installed"
        else
            echo -e "${YELLOW}📦${NC} Installing $package..."
            sudo apt install -y "$package"
            echo -e "${GREEN}✓${NC} $package installed successfully"
        fi
    done
    
    echo
}

# Configure firewall
configure_firewall() {
    log "INFO" "Configuring firewall..."
    
    echo -e "${BLUE}🔥 Configuring UFW firewall...${NC}"
    
    # Reset UFW to defaults
    sudo ufw --force reset
    
    # Default policies
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    
    # Allow SSH (be careful with this)
    sudo ufw allow ssh
    
    # Allow web traffic
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    
    # Allow application ports
    sudo ufw allow 8000/tcp comment 'BrainSAIT Backend API'
    sudo ufw allow 5173/tcp comment 'BrainSAIT Frontend Dev'
    sudo ufw allow 3000/tcp comment 'BrainSAIT Frontend Prod'
    
    # Allow database access (only from localhost)
    sudo ufw allow from 127.0.0.1 to any port 5432 comment 'PostgreSQL localhost'
    sudo ufw allow from 127.0.0.1 to any port 6379 comment 'Redis localhost'
    
    # Enable firewall
    sudo ufw --force enable
    
    echo -e "${GREEN}✓${NC} Firewall configured successfully"
    sudo ufw status verbose
    echo
}

# Configure fail2ban
configure_fail2ban() {
    log "INFO" "Configuring fail2ban..."
    
    echo -e "${BLUE}🛡️ Configuring fail2ban intrusion prevention...${NC}"
    
    # Create custom jail configuration
    sudo tee /etc/fail2ban/jail.local > /dev/null << EOF
[DEFAULT]
# Ban hosts for 1 hour
bantime = 3600

# A host is banned if it generates 5 failures over 10 minutes
findtime = 600
maxretry = 5

# Email notifications
destemail = admin@brainsait.com
sender = fail2ban@brainsait.com
mta = sendmail

# Actions
action = %(action_mwl)s

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
filter = nginx-badbots
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-noproxy]
enabled = true
port = http,https
filter = nginx-noproxy
logpath = /var/log/nginx/access.log
maxretry = 2
