#!/bin/bash

# 🛡️ BrainSAIT Healthcare Platform - Copilot Security Setup Script
# Configure GitHub Copilot firewall for HIPAA and NPHIES compliance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_OWNER="Fadil369"
REPO_NAME="brainsait-unified-ecosystem"

echo -e "${BLUE}🏥 BrainSAIT Healthcare Platform - Copilot Security Configuration${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed. Please install it first.${NC}"
    echo "Visit: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  You need to authenticate with GitHub CLI first.${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI is installed and authenticated${NC}"
echo ""

# Healthcare-specific allowlist domains
declare -a HEALTHCARE_DOMAINS=(
    # NPHIES (Saudi National Platform for Health Information Exchange)
    "nphies.sa"
    "api.nphies.sa"
    "portal.nphies.sa"
    "services.nphies.sa"
    
    # HL7 FHIR Standards
    "hl7.org"
    "fhir.org"
    "terminology.hl7.org"
    "build.fhir.org"
    
    # Saudi Healthcare Authorities
    "moh.gov.sa"
    "api.moh.gov.sa"
    "shc.gov.sa"
    "sfda.gov.sa"
    
    # Secure Package Repositories
    "pypi.org"
    "files.pythonhosted.org"
    "registry.npmjs.org"
    "npm.pkg.github.com"
    "ghcr.io"
    
    # HIPAA-Compliant Services
    "api.twilio.com"
    "voice.twilio.com"
    "video.twilio.com"
    
    # Healthcare Compliance Resources
    "hhs.gov"
    "hipaa.com"
    
    # GitHub Services
    "github.com"
    "api.github.com"
    "raw.githubusercontent.com"
)

# Healthcare-specific URL allowlist (more restrictive)
declare -a HEALTHCARE_URLS=(
    # NPHIES specific endpoints
    "https://api.nphies.sa/eligibility/"
    "https://api.nphies.sa/preauthorization/"
    "https://api.nphies.sa/claim/"
    "https://portal.nphies.sa/provider/"
    
    # HL7 FHIR R4 resources
    "https://hl7.org/fhir/R4/"
    "https://terminology.hl7.org/fhir/"
    "https://build.fhir.org/ig/"
    
    # Saudi MOH APIs
    "https://api.moh.gov.sa/v1/"
    "https://moh.gov.sa/en/Ministry/"
    
    # Twilio HIPAA BAA endpoints
    "https://api.twilio.com/2010-04-01/"
    "https://voice.twilio.com/v1/"
    "https://video.twilio.com/v1/"
    
    # Package repositories (healthcare packages only)
    "https://pypi.org/project/fhir/"
    "https://pypi.org/project/hl7/"
    "https://pypi.org/project/healthcare/"
    "https://registry.npmjs.org/@types/fhir"
)

echo -e "${YELLOW}📋 Healthcare Domains to Allowlist:${NC}"
for domain in "${HEALTHCARE_DOMAINS[@]}"; do
    echo -e "   • $domain"
done
echo ""

echo -e "${YELLOW}📋 Healthcare URLs to Allowlist:${NC}"
for url in "${HEALTHCARE_URLS[@]}"; do
    echo -e "   • $url"
done
echo ""

# Confirm with user
read -p "Do you want to proceed with configuring Copilot security? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  Configuration cancelled by user.${NC}"
    exit 0
fi

echo -e "${BLUE}🔧 Configuring Copilot firewall settings...${NC}"

# Note: GitHub CLI doesn't have direct Copilot firewall configuration commands yet
# We'll provide manual configuration instructions

echo -e "${GREEN}✅ Configuration Instructions:${NC}"
echo ""
echo -e "${YELLOW}Manual Configuration Required:${NC}"
echo "GitHub CLI doesn't support Copilot firewall configuration yet."
echo "Please follow these steps manually:"
echo ""

echo -e "${BLUE}Step 1: Access Repository Settings${NC}"
echo "1. Navigate to: https://github.com/${REPO_OWNER}/${REPO_NAME}"
echo "2. Go to Settings → Code & automation → Copilot → Coding agent"
echo ""

echo -e "${BLUE}Step 2: Configure Firewall${NC}"
echo "1. Ensure 'Enable firewall' is ON"
echo "2. Keep 'Recommended allowlist' ON"
echo "3. Click 'Custom allowlist'"
echo ""

echo -e "${BLUE}Step 3: Add Healthcare Domains${NC}"
echo "Add these domains one by one:"
for domain in "${HEALTHCARE_DOMAINS[@]}"; do
    echo "   → $domain"
done
echo ""

echo -e "${BLUE}Step 4: Add Healthcare URLs${NC}"
echo "Add these URLs for more restrictive access:"
for url in "${HEALTHCARE_URLS[@]}"; do
    echo "   → $url"
done
echo ""

# Create configuration backup file
cat > .copilot-healthcare-config.json << EOF
{
  "copilot_firewall_config": {
    "enabled": true,
    "recommended_allowlist": true,
    "custom_allowlist": {
      "domains": [
$(printf '        "%s",\n' "${HEALTHCARE_DOMAINS[@]}" | sed '$ s/,$//')
      ],
      "urls": [
$(printf '        "%s",\n' "${HEALTHCARE_URLS[@]}" | sed '$ s/,$//')
      ]
    },
    "last_updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "compliance": {
      "hipaa": true,
      "nphies": true,
      "saudi_healthcare": true
    }
  }
}
EOF

echo -e "${GREEN}✅ Configuration backup saved to: .copilot-healthcare-config.json${NC}"
echo ""

# Create monitoring script
cat > monitor-copilot-security.sh << 'EOF'
#!/bin/bash

# 🔍 Monitor Copilot Security Warnings
# Run this script to check for firewall warnings in recent PRs

REPO_OWNER="Fadil369"
REPO_NAME="brainsait-unified-ecosystem"

echo "🔍 Checking recent PRs for Copilot firewall warnings..."

# Get recent PRs
recent_prs=$(gh pr list --repo "$REPO_OWNER/$REPO_NAME" --limit 10 --json number,title,body)

# Check for firewall warnings
echo "$recent_prs" | jq -r '.[] | select(.body | contains("blocked by the firewall")) | "PR #\(.number): \(.title)"'

# Check PR comments for warnings
echo "🔍 Checking PR comments for firewall warnings..."
gh pr list --repo "$REPO_OWNER/$REPO_NAME" --limit 5 --json number | jq -r '.[].number' | while read pr_number; do
    comments=$(gh pr view "$pr_number" --repo "$REPO_OWNER/$REPO_NAME" --comments --json comments)
    warnings=$(echo "$comments" | jq -r '.comments[] | select(.body | contains("blocked by the firewall")) | .body')
    if [ ! -z "$warnings" ]; then
        echo "⚠️  Firewall warning found in PR #$pr_number:"
        echo "$warnings"
        echo "---"
    fi
done

echo "✅ Security monitoring complete."
EOF

chmod +x monitor-copilot-security.sh

echo -e "${GREEN}✅ Monitoring script created: monitor-copilot-security.sh${NC}"
echo ""

# Security checklist
echo -e "${BLUE}🔒 Security Checklist:${NC}"
echo "□ Firewall is enabled"
echo "□ Recommended allowlist is enabled"
echo "□ Healthcare domains are allowlisted"
echo "□ Team is trained on firewall warnings"
echo "□ Incident response plan is documented"
echo "□ Regular monitoring is scheduled"
echo ""

# HIPAA compliance reminder
echo -e "${RED}🚨 HIPAA COMPLIANCE REMINDER:${NC}"
echo "• NEVER disable the Copilot firewall for healthcare repositories"
echo "• Monitor firewall warnings weekly"
echo "• Document all allowlist changes"
echo "• Report security incidents within 1 hour"
echo "• Review configuration monthly"
echo ""

echo -e "${GREEN}🎉 Copilot security configuration guide complete!${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Follow the manual configuration steps above"
echo "2. Run ./monitor-copilot-security.sh weekly"
echo "3. Review .copilot-healthcare-config.json for compliance"
echo "4. Update your security documentation"
echo ""

echo -e "${BLUE}📞 Support:${NC}"
echo "Security Issues: security@brainsait.com"
echo "Healthcare Compliance: compliance@brainsait.com"
echo ""
