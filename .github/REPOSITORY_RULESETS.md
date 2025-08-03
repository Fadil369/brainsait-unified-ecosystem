# 🛡️ Repository Rulesets and Protection Configuration

## Overview

This document describes the comprehensive repository protection rules implemented for the BrainSAIT Unified Healthcare Ecosystem. These rules ensure security, compliance, and quality standards for our healthcare platform that handles sensitive patient data and must comply with HIPAA, NPHIES, and Saudi healthcare regulations.

## 📋 Files in This Configuration

### 1. `.github/repository-ruleset.json`
**Primary repository ruleset** defining core protection rules for branch management, code quality, and security compliance.

### 2. `.github/repository-config.json`
**Extended configuration** including branch protection rules, environment settings, and Dependabot configuration.

### 3. `.github/CODEOWNERS`
**Code ownership definitions** specifying which teams must review changes to different parts of the codebase.

## 🏥 Healthcare-Specific Protection Rules

### HIPAA Compliance Rules
- **Patient Data Protection**: Restricted access to files containing PHI (Protected Health Information)
- **Audit Trail Requirements**: All commits affecting patient data must include audit trails
- **Security Review**: Healthcare-related changes require security team approval

### NPHIES Integration Protection
- **Saudi Healthcare Standards**: Special protection for NPHIES integration files
- **Compliance Validation**: Required status checks for Saudi healthcare compliance
- **Medical Data Security**: Enhanced protection for medical record handling

### Arabic Language Support
- **RTL Layout Testing**: Required accessibility and Arabic RTL testing
- **Internationalization Review**: Arabic language team approval for i18n changes
- **Cultural Compliance**: Validation of Arabic medical terminology and cultural adaptations

## 🔒 Security and Access Control

### Branch Protection Levels

#### Main Branch (Production)
- ✅ **2 Required Approvals** from different team members
- ✅ **All Status Checks Must Pass** (13 different security and quality checks)
- ✅ **Code Owner Review Required** for all changes
- ✅ **Signed Commits Required** for audit trail
- ✅ **Linear History Required** for clean git history
- ❌ **No Force Pushes** to prevent history rewriting
- ❌ **No Branch Deletion** to maintain production stability

#### Develop Branch (Development)
- ✅ **1 Required Approval** for faster development
- ✅ **Core Status Checks** (4 essential checks)
- ❌ **No Force Pushes** to maintain development stability

#### Release Branches (Release Management)
- ✅ **3 Required Approvals** for production releases
- ✅ **Extended Status Checks** including performance testing
- ✅ **Release Manager Approval** required
- ✅ **Security Team Approval** required

#### Hotfix Branches (Emergency Fixes)
- ✅ **2 Required Approvals** for emergency changes
- ✅ **Security Compliance Checks** for rapid deployment
- ✅ **Emergency Team Review** for critical fixes

### File Path Restrictions

#### Protected File Types
```json
[
  "backend/config/production.py",    // Production configuration
  "backend/.env.production",         // Production environment variables
  "backend/keys/*",                  // Encryption keys
  "backend/secrets/*",               // Secret files
  "ssl/*",                          // SSL certificates
  "*.pem", "*.key", "*.p12",        // Security certificates
  "*.pfx", "*.jks"                  // Keystore files
]
```

#### Restricted File Extensions
```json
[
  ".env",        // Environment files
  ".key",        // Private keys
  ".pem",        // Certificate files
  ".secret"      // Secret files
]
```

### File Size and Path Limits
- **Maximum File Size**: 100 MB (104,857,600 bytes)
- **Maximum Path Length**: 255 characters
- **Binary File Restrictions**: Large binary files require special approval

## 🚀 Required Status Checks

### Core Security Checks
1. **🔒 Security & Compliance Scan** - Bandit security analysis
2. **🛡️ Dependency Vulnerability Scan** - Safety and npm audit
3. **🔍 Static Code Security Analysis** - Semgrep multi-language analysis
4. **🚨 SAST - CodeQL Analysis** - GitHub's semantic code analysis
5. **🔐 Secrets & Credential Scanning** - TruffleHog and GitLeaks

### Healthcare Compliance Checks
6. **🏥 Healthcare Compliance Validation** - FHIR R4 and medical standards
7. **🏥 Healthcare Security Compliance** - HIPAA and patient data protection

### Quality and Testing Checks
8. **🐍 Backend Tests** - Python application testing
9. **⚛️ Frontend Tests** - React application testing
10. **🔄 Integration Tests** - End-to-end system testing
11. **🌐 Accessibility & Arabic RTL Testing** - UI accessibility and Arabic support
12. **🐳 Docker Build & Security Scan** - Container security with Trivy

### Additional Checks (for releases)
13. **📊 Performance Testing** - Load and performance validation

## 👥 Team Structure and Code Ownership

### Core Teams
- **@brainsait/core-developers** - Primary development team
- **@brainsait/security-team** - Security and compliance oversight
- **@brainsait/healthcare-team** - Medical domain expertise
- **@brainsait/compliance-team** - HIPAA and regulatory compliance

### Specialized Teams
- **@brainsait/arabic-team** - Arabic language and RTL support
- **@brainsait/ai-team** - AI and machine learning features
- **@brainsait/nphies-team** - Saudi NPHIES integration
- **@brainsait/devops-team** - Infrastructure and deployment

### Emergency Response Teams
- **@brainsait/emergency-team** - Critical issue response
- **@brainsait/hotfix-team** - Emergency deployment authorization

## 🔄 Commit Message Standards

### Required Format
```
type(scope): description

Examples:
feat(nphies): add patient eligibility verification
fix(arabic): resolve RTL layout issues in forms
security(hipaa): enhance patient data encryption
healthcare(compliance): update audit logging
```

### Valid Types
- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation changes
- `security` - Security improvements
- `healthcare` - Healthcare-specific changes
- `hipaa` - HIPAA compliance updates
- `nphies` - NPHIES integration changes
- `arabic` - Arabic language support

### Email Requirements
**Approved Domains:**
- `@brainsait.com` - Company email addresses
- `@github.com` - GitHub email addresses
- `@users.noreply.github.com` - GitHub no-reply addresses

## 🌍 Environment Protection

### Production Environment
- **Required Reviewers**: Security team, Healthcare compliance, DevOps team
- **Deployment Branches**: Only protected branches (main, release/*)
- **Wait Timer**: 5 minutes cooling-off period
- **Admin Bypass**: Disabled for maximum security

### Staging Environment
- **Required Reviewers**: QA team, Healthcare team
- **Deployment Branches**: develop, release/* branches
- **Wait Timer**: 2 minutes
- **Admin Bypass**: Enabled for development flexibility

## 🤖 Automated Dependency Management

### Dependabot Configuration
- **Python Dependencies**: Weekly updates on Mondays (Asia/Riyadh timezone)
- **Node.js Dependencies**: Weekly updates on Tuesdays
- **Docker Images**: Weekly updates on Wednesdays
- **GitHub Actions**: Weekly updates on Thursdays

### Security-First Approach
- All dependency updates target `develop` branch first
- Security team review required for all updates
- Automatic labeling for easy categorization
- Limited concurrent PRs to prevent overwhelm

## 📝 Implementation Instructions

### 1. Apply Repository Ruleset
```bash
# Using GitHub CLI
gh api repos/Fadil369/brainsait-unified-ecosystem/rulesets \
  --method POST \
  --input .github/repository-ruleset.json
```

### 2. Configure Branch Protection
```bash
# Apply to main branch
gh api repos/Fadil369/brainsait-unified-ecosystem/branches/main/protection \
  --method PUT \
  --input branch-protection-config.json
```

### 3. Set Up Code Owners
The `.github/CODEOWNERS` file is automatically recognized by GitHub and will:
- Require reviews from specified teams
- Auto-assign reviewers based on file changes
- Enforce ownership hierarchy

### 4. Configure Security Settings
Enable in GitHub repository settings:
- ✅ Vulnerability alerts
- ✅ Automated security fixes
- ✅ Dependency scanning
- ✅ Code scanning
- ✅ Secret scanning
- ✅ Secret scanning push protection

## 🚨 Emergency Procedures

### Critical Security Issues
1. **Immediate Response**: Emergency team can bypass some restrictions
2. **Security Team Notification**: Automatic alerts for security violations
3. **Audit Trail**: All emergency actions are logged and reviewed

### Healthcare Compliance Violations
1. **Automatic Blocking**: Commits affecting patient data without proper approval
2. **Compliance Team Review**: Required for all healthcare-related changes
3. **Audit Documentation**: Comprehensive logging for regulatory compliance

### Production Hotfixes
1. **Emergency Team Authorization**: Required for production hotfixes
2. **Accelerated Review**: Streamlined approval process for critical fixes
3. **Post-Deployment Review**: Mandatory security review after emergency deployments

## 📊 Monitoring and Reporting

### Metrics Tracked
- **Security Scan Results**: Daily vulnerability reports
- **Compliance Status**: HIPAA and NPHIES compliance metrics
- **Code Quality**: Test coverage and code quality trends
- **Team Performance**: Review response times and approval rates

### Regular Reviews
- **Weekly**: Security scan results and dependency updates
- **Monthly**: Rule effectiveness and team performance
- **Quarterly**: Comprehensive security and compliance audit

## 🔗 Related Documentation

- [SECURITY.md](../SECURITY.md) - Security policies and procedures
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guidelines
- [SECURITY_ADVISORY.md](../SECURITY_ADVISORY.md) - Security issue resolution
- [README.md](../README.md) - Project overview and setup

## 📞 Support and Contact

### Security Issues
- **Email**: security@brainsait.com
- **Slack**: #security-alerts
- **Emergency**: Contact emergency team directly

### Healthcare Compliance
- **Email**: compliance@brainsait.com
- **Slack**: #healthcare-compliance

### Technical Support
- **Email**: devops@brainsait.com
- **Slack**: #devops-support

---

*This configuration ensures that our healthcare platform maintains the highest standards of security, compliance, and quality while supporting efficient development workflows for our distributed team.*
