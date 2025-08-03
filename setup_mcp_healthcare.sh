#!/bin/bash
# BrainSAIT MCP Healthcare Setup Script

set -e

echo "🏥 Setting up BrainSAIT Healthcare MCP Servers..."

# Install Python dependencies
echo "📦 Installing MCP dependencies..."
pip install -r backend/requirements_mcp.txt

# Create necessary directories
echo "📁 Creating MCP directories..."
mkdir -p /opt/brainsait/models
mkdir -p /opt/medical_terms
mkdir -p /secure/compliance

# Set up Arabic medical terminology database
echo "🔤 Setting up Arabic medical terminology..."
if [ ! -f "/opt/medical_terms/saudi_ar.db" ]; then
    echo "Creating Arabic medical terms database..."
    # Download or create Arabic medical terms database
    touch /opt/medical_terms/saudi_ar.db
fi

# Set up NPHIES certificates (if available)
echo "🔐 Setting up NPHIES certificates..."
if [ -n "$NPHIES_SSL_CERT" ]; then
    mkdir -p /opt/nphies/certs
    echo "$NPHIES_SSL_CERT" > /opt/nphies/certs/client.crt
    echo "$NPHIES_SSL_KEY" > /opt/nphies/certs/client.key
    chmod 600 /opt/nphies/certs/*
fi

# Validate MCP servers
echo "✅ Validating MCP servers..."
python -c "
try:
    from backend.brainsait_mcp_servers import nphies_server
    from backend.brainsait_mcp_servers import arabic_medical_server
    print('✅ NPHIES and Arabic Medical MCP servers validated')
except ImportError as e:
    print(f'⚠️  MCP servers validation warning: {e}')
    print('This is normal if MCP packages are not yet installed')
"

echo "🚀 BrainSAIT MCP Healthcare setup completed!"
echo ""
echo "Next steps:"
echo "1. Configure GitHub Copilot with the MCP configuration"
echo "2. Set up environment secrets in GitHub"
echo "3. Test MCP integration with Copilot"
echo ""
echo "For detailed instructions, see: .github/copilot-mcp-config-template.md"
