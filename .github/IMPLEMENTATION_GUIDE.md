# 🚀 Repository Rulesets Implementation Guide

## Quick Start - Applying Rulesets to Your Repository

### Prerequisites
- GitHub CLI installed (`gh`)
- Repository admin access
- GitHub Enterprise or GitHub.com (rulesets require certain plan levels)

### 1. Apply Repository Ruleset (Primary Protection)

```bash
# Navigate to your repository
cd /path/to/brainsait-unified-ecosystem

# Apply the main ruleset using GitHub CLI
gh api repos/Fadil369/brainsait-unified-ecosystem/rulesets \
  --method POST \
  --input .github/repository-ruleset.json
```

### 2. Configure Branch Protection Rules

```bash
# Apply main branch protection
gh api repos/Fadil369/brainsait-unified-ecosystem/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["🔒 Security & Compliance Scan","🐍 Backend Tests","⚛️ Frontend Tests","🔄 Integration Tests","🏥 Healthcare Compliance Validation","🐳 Docker Build & Security Scan","🌐 Accessibility & Arabic RTL Testing","🛡️ Dependency Vulnerability Scan","🔍 Static Code Security Analysis","🚨 SAST - CodeQL Analysis (javascript)","🚨 SAST - CodeQL Analysis (python)","🏥 Healthcare Security Compliance","🔐 Secrets & Credential Scanning"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":2,"require_last_push_approval":true}' \
  --field required_linear_history=true \
  --field allow_force_pushes=false \
  --field allow_deletions=false \
  --field required_signatures=true
```

### 3. Enable Security Features

```bash
# Enable vulnerability alerts
gh api repos/Fadil369/brainsait-unified-ecosystem/vulnerability-alerts \
  --method PUT

# Enable automated security fixes
gh api repos/Fadil369/brainsait-unified-ecosystem/automated-security-fixes \
  --method PUT

# Enable secret scanning
gh api repos/Fadil369/brainsait-unified-ecosystem \
  --method PATCH \
  --field security_and_analysis='{"secret_scanning":{"status":"enabled"},"secret_scanning_push_protection":{"status":"enabled"}}'
```

### 4. Configure Dependabot

Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "Asia/Riyadh"
    labels:
      - "security"
      - "dependencies"
      - "healthcare"
    reviewers:
      - "@brainsait/security-team"
    
  - package-ecosystem: "npm"
    directory: "/oid-portal"
    schedule:
      interval: "weekly"
      day: "tuesday"
      time: "10:00"
      timezone: "Asia/Riyadh"
    labels:
      - "security"
      - "dependencies"
      - "frontend"
    reviewers:
      - "@brainsait/frontend-team"
```

## 🎯 Alternative Manual Configuration

### Via GitHub Web Interface

#### 1. Repository Settings
1. Go to `Settings` → `General`
2. Configure merge settings:
   - ✅ Allow squash merging
   - ✅ Allow rebase merging  
   - ❌ Allow merge commits
   - ✅ Automatically delete head branches

#### 2. Branch Protection Rules
1. Go to `Settings` → `Branches`
2. Add rule for `main`:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (2)
   - ✅ Dismiss stale reviews
   - ✅ Require review from CODEOWNERS
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
   - ✅ Require linear history
   - ✅ Include administrators
   - ❌ Allow force pushes
   - ❌ Allow deletions

#### 3. Security Settings
1. Go to `Settings` → `Security & analysis`
2. Enable all security features:
   - ✅ Vulnerability alerts
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates
   - ✅ Secret scanning
   - ✅ Push protection for secret scanning

#### 4. Actions Settings
1. Go to `Settings` → `Actions` → `General`
2. Configure permissions:
   - ✅ Allow enterprise and select non-enterprise actions
   - ✅ Allow actions created by GitHub
   - ✅ Allow specified actions

## 🔧 Team Setup Requirements

### Create GitHub Teams
```bash
# Core teams
gh api orgs/brainsait/teams --method POST --field name="core-developers" --field description="Core development team"
gh api orgs/brainsait/teams --method POST --field name="security-team" --field description="Security and compliance team"
gh api orgs/brainsait/teams --method POST --field name="healthcare-team" --field description="Healthcare domain experts"
gh api orgs/brainsait/teams --method POST --field name="compliance-team" --field description="HIPAA and regulatory compliance"

# Specialized teams
gh api orgs/brainsait/teams --method POST --field name="arabic-team" --field description="Arabic language and RTL support"
gh api orgs/brainsait/teams --method POST --field name="ai-team" --field description="AI and machine learning features"
gh api orgs/brainsait/teams --method POST --field name="nphies-team" --field description="Saudi NPHIES integration"
gh api orgs/brainsait/teams --method POST --field name="devops-team" --field description="Infrastructure and deployment"
```

### Add Team Members
```bash
# Add members to teams
gh api orgs/brainsait/teams/core-developers/memberships/username --method PUT --field role=member
gh api orgs/brainsait/teams/security-team/memberships/username --method PUT --field role=member
# ... repeat for other teams
```

## 📋 Verification Checklist

### ✅ Repository Configuration
- [ ] Repository ruleset applied successfully
- [ ] Branch protection rules configured
- [ ] CODEOWNERS file recognized by GitHub
- [ ] Security features enabled
- [ ] Dependabot configured

### ✅ Team Setup
- [ ] GitHub teams created
- [ ] Team members added
- [ ] Repository permissions assigned
- [ ] Code review assignments working

### ✅ Workflow Integration
- [ ] Status checks aligned with rulesets
- [ ] CI/CD workflows passing
- [ ] Security scans executing
- [ ] Healthcare compliance checks active

### ✅ Testing Protection Rules
- [ ] Create test branch and PR
- [ ] Verify required approvals
- [ ] Test status check requirements
- [ ] Validate CODEOWNERS assignments
- [ ] Confirm file path restrictions

## 🚨 Troubleshooting

### Common Issues

#### Ruleset Not Applied
```bash
# Check existing rulesets
gh api repos/Fadil369/brainsait-unified-ecosystem/rulesets

# Update existing ruleset
gh api repos/Fadil369/brainsait-unified-ecosystem/rulesets/RULESET_ID \
  --method PUT \
  --input .github/repository-ruleset.json
```

#### Status Checks Not Matching
1. Check workflow job names match status check contexts
2. Update workflow names if needed
3. Verify branch protection rule status check list

#### Team Permissions Issues
```bash
# Check team permissions
gh api repos/Fadil369/brainsait-unified-ecosystem/teams

# Add team to repository
gh api repos/Fadil369/brainsait-unified-ecosystem/teams/TEAM_NAME \
  --method PUT \
  --field permission=push
```

### Emergency Override Procedures

#### Temporary Rule Bypass
```bash
# Disable ruleset temporarily (admin only)
gh api repos/Fadil369/brainsait-unified-ecosystem/rulesets/RULESET_ID \
  --method PATCH \
  --field enforcement=disabled

# Re-enable after emergency
gh api repos/Fadil369/brainsait-unified-ecosystem/rulesets/RULESET_ID \
  --method PATCH \
  --field enforcement=active
```

## 📊 Monitoring and Maintenance

### Regular Tasks
- **Weekly**: Review security scan results and dependency updates
- **Monthly**: Audit rule effectiveness and team performance
- **Quarterly**: Update rulesets based on new requirements

### Metrics to Track
- Pull request approval times
- Security scan failure rates
- Compliance check success rates
- Emergency override usage

## 🔗 Additional Resources

- [GitHub Rulesets Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets)
- [Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [CODEOWNERS Documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [Security Features Documentation](https://docs.github.com/en/code-security)

---

*This implementation guide provides step-by-step instructions for applying enterprise-grade repository protection to your healthcare platform. Follow the steps carefully to ensure proper security and compliance coverage.*
