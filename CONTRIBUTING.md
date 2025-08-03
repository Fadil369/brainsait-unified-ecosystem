# Contributing to BrainSAIT Unified Healthcare Ecosystem

Thank you for your interest in contributing to the BrainSAIT Unified Healthcare Ecosystem! This project is committed to providing a world-class healthcare platform for Saudi Arabia's healthcare sector, and we welcome contributions from developers, healthcare professionals, and security experts worldwide.

## 🌟 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Healthcare Compliance Guidelines](#healthcare-compliance-guidelines)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Arabic Language Guidelines](#arabic-language-guidelines)
- [Security Considerations](#security-considerations)
- [Documentation Standards](#documentation-standards)

## 📋 Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. By participating, you agree to uphold this code.

### Our Pledge

- **Respectful**: We treat everyone with respect and dignity
- **Inclusive**: We welcome contributors from all backgrounds
- **Professional**: We maintain professional standards in all interactions
- **Healthcare-Focused**: We prioritize patient safety and data privacy
- **Cultural Sensitivity**: We respect Arabic culture and Saudi healthcare practices

## 🤝 How Can I Contribute?

### 🐛 Reporting Bugs

Before submitting a bug report:

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** when creating new issues
3. **Include healthcare context** if the bug affects patient care
4. **Provide Arabic text examples** if relevant to Arabic language features

**Bug Report Requirements:**
- Clear description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, browser, etc.)
- Screenshots or screen recordings
- Impact on healthcare workflows (if applicable)

### ✨ Suggesting Enhancements

Enhancement suggestions are welcome! Consider:

- **Healthcare workflow improvements**
- **NPHIES compliance enhancements**
- **Arabic language features**
- **Security improvements**
- **Performance optimizations**
- **User experience enhancements**

### 💻 Code Contributions

We welcome the following types of code contributions:

- **Bug fixes** for existing functionality
- **New healthcare features** aligned with our roadmap
- **Arabic localization** improvements
- **Security enhancements**
- **Performance optimizations**
- **Test coverage** improvements
- **Documentation** updates

## 🛠️ Development Setup

### Prerequisites

- **Python 3.11+** with virtual environment support
- **Node.js 18+** with npm
- **Docker & Docker Compose**
- **PostgreSQL 15+**
- **Git** with proper configuration

### Local Development Environment

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/brainsait-unified-ecosystem.git
cd brainsait-unified-ecosystem

# 2. Set up backend environment
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python init_platform.py

# 3. Set up frontend environment
cd ../oid-portal
npm install
cp .env.example .env.local

# 4. Start development servers
# Terminal 1 - Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd oid-portal && npm run dev
```

### Docker Development

```bash
# Start complete development stack
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f

# Access containers
docker-compose exec backend bash
docker-compose exec frontend bash
```

## 📝 Coding Standards

### Python (Backend)

```python
# Follow PEP 8 style guide
# Use type hints for all functions
# Include comprehensive docstrings

from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class HealthcareIdentity(BaseModel):
    """Healthcare identity model compliant with NPHIES standards."""
    
    patient_id: str
    national_id: str
    name_arabic: str
    name_english: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "patient_id": "PAT001",
                "national_id": "1234567890",
                "name_arabic": "محمد أحمد",
                "name_english": "Mohammed Ahmed"
            }
        }

async def create_patient(patient: HealthcareIdentity) -> dict:
    """
    Create a new patient record with NPHIES compliance.
    
    Args:
        patient: Patient data following NPHIES standards
        
    Returns:
        dict: Created patient record with OID
        
    Raises:
        HTTPException: If validation fails or NPHIES error occurs
    """
    # Implementation here
    pass
```

### JavaScript/React (Frontend)

```javascript
// Use functional components with hooks
// Include PropTypes or TypeScript
// Follow React best practices

import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useLanguage } from '../contexts/LanguageContext';

/**
 * Healthcare identity component with Arabic RTL support
 * @param {Object} props - Component props
 * @param {string} props.patientId - Patient identifier
 * @param {Function} props.onUpdate - Update callback
 */
const HealthcareIdentityCard = ({ patientId, onUpdate }) => {
  const { language, isRTL } = useLanguage();
  const [patientData, setPatientData] = useState(null);
  
  useEffect(() => {
    // Fetch patient data with Arabic support
    fetchPatientData(patientId);
  }, [patientId]);
  
  return (
    <div className={`patient-card ${isRTL ? 'rtl' : 'ltr'}`}>
      {/* Component implementation */}
    </div>
  );
};

HealthcareIdentityCard.propTypes = {
  patientId: PropTypes.string.isRequired,
  onUpdate: PropTypes.func.isRequired,
};

export default HealthcareIdentityCard;
```

### Code Quality Tools

```bash
# Python linting and formatting
black backend/
flake8 backend/
mypy backend/

# JavaScript linting and formatting
npm run lint
npm run format
npm run type-check

# Security scanning
bandit -r backend/
npm audit

# Test coverage
pytest --cov=backend/
npm run test -- --coverage
```

## 🏥 Healthcare Compliance Guidelines

### NPHIES Integration Standards

When working with NPHIES-related code:

```python
# Always use proper NPHIES identifiers
NPHIES_PATIENT_ID_PATTERN = r'^PAT\d{6,}$'
NPHIES_PROVIDER_ID_PATTERN = r'^PRV\d{6,}$'

# Include proper error handling for NPHIES APIs
try:
    response = await nphies_client.submit_claim(claim_data)
except NPHIESError as e:
    logger.error(f"NPHIES submission failed: {e.error_code}")
    raise HTTPException(
        status_code=422,
        detail=f"NPHIES validation error: {e.message}"
    )
```

### HIPAA Compliance

- **Never log patient data** in plain text
- **Use encrypted storage** for all patient information
- **Implement audit trails** for all data access
- **Follow minimum necessary** access principles

```python
# Good: Logging without patient data
logger.info(f"Patient record accessed: {hash(patient_id)}")

# Bad: Logging patient data
logger.info(f"Patient accessed: {patient_name}")  # DON'T DO THIS
```

### Data Privacy Guidelines

- **Anonymize test data** - Never use real patient information
- **Encrypt sensitive data** at rest and in transit
- **Implement data retention** policies
- **Support data deletion** requests (Right to be Forgotten)

## 🧪 Testing Requirements

### Test Coverage Requirements

- **Backend**: Minimum 90% code coverage
- **Frontend**: Minimum 80% code coverage
- **Integration tests**: All critical healthcare workflows
- **Security tests**: OWASP Top 10 coverage

### Healthcare-Specific Testing

```python
# Test NPHIES compliance
def test_nphies_patient_registration():
    """Test patient registration with NPHIES standards."""
    patient_data = {
        "national_id": "1234567890",
        "name_arabic": "محمد أحمد",
        "birth_date": "1990-01-01",
    }
    
    response = client.post("/api/patients", json=patient_data)
    
    assert response.status_code == 201
    assert "patient_oid" in response.json()
    assert validate_nphies_format(response.json()["patient_oid"])

# Test Arabic language support
def test_arabic_patient_search():
    """Test patient search with Arabic names."""
    search_term = "محمد"
    response = client.get(f"/api/patients/search?q={search_term}")
    
    assert response.status_code == 200
    assert len(response.json()["results"]) > 0
```

### Frontend Testing

```javascript
// Test Arabic RTL support
describe('Arabic RTL Support', () => {
  test('should render patient card with RTL layout', () => {
    const { container } = render(
      <LanguageProvider language="ar">
        <HealthcareIdentityCard patientId="PAT001" />
      </LanguageProvider>
    );
    
    expect(container.querySelector('.patient-card')).toHaveClass('rtl');
  });
});
```

## 📥 Pull Request Process

### Before Submitting

1. **Create feature branch** from `main`
2. **Write comprehensive tests** for new functionality
3. **Update documentation** as needed
4. **Test Arabic language features** if applicable
5. **Run security scans** and fix any issues
6. **Verify NPHIES compliance** for healthcare features

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Healthcare workflow improvement
- [ ] Arabic language enhancement
- [ ] Security improvement
- [ ] Documentation update

## Healthcare Impact
- [ ] Affects patient data handling
- [ ] Changes NPHIES integration
- [ ] Modifies clinical workflows
- [ ] Updates compliance features

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Arabic language testing completed
- [ ] Security testing completed
- [ ] Manual testing completed

## Compliance Checklist
- [ ] HIPAA compliance verified
- [ ] NPHIES standards followed
- [ ] Saudi PDPL requirements met
- [ ] Security review completed

## Screenshots/Videos
Include relevant screenshots or videos for UI changes
```

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by at least 2 maintainers
3. **Healthcare expert review** for clinical features
4. **Security review** for security-sensitive changes
5. **Arabic language review** for localization changes

## 🌐 Arabic Language Guidelines

### Text Handling

```javascript
// Support both Arabic and English text
const displayName = (patient) => {
  const { language } = useLanguage();
  return language === 'ar' ? patient.name_arabic : patient.name_english;
};

// Handle RTL text properly
const formatAddress = (address) => {
  return {
    ...address,
    direction: detectTextDirection(address.text)
  };
};
```

### UI Components

- **Use semantic HTML** for proper RTL support
- **Test with Arabic fonts** (Noto Sans Arabic, Cairo)
- **Verify RTL layouts** in all screen sizes
- **Include Arabic placeholder text** in forms

### Translation Guidelines

- **Use proper Arabic medical terminology**
- **Maintain consistency** with Saudi healthcare standards
- **Consider cultural context** in UI messages
- **Provide context** for translators

## 🔒 Security Considerations

### Security Requirements

- **Input validation** for all user inputs
- **SQL injection prevention** using parameterized queries
- **XSS protection** with proper output encoding
- **CSRF protection** for state-changing operations
- **Authentication** for all protected endpoints
- **Authorization** with role-based access control

### Security Testing

```bash
# Run security scans before submitting PR
bandit -r backend/
npm audit
docker scan

# Test authentication and authorization
pytest backend/tests/test_security.py

# Verify HTTPS enforcement
curl -I http://localhost:8000/api/health
```

## 📚 Documentation Standards

### Code Documentation

- **Docstrings** for all Python functions and classes
- **JSDoc comments** for JavaScript functions
- **Type annotations** for better code understanding
- **README updates** for new features

### API Documentation

- **OpenAPI specifications** for all endpoints
- **Example requests/responses** with Arabic content
- **Error code documentation** with healthcare context
- **Integration guides** for NPHIES features

### User Documentation

- **Arabic translations** for all user-facing content
- **Healthcare workflow guides** with screenshots
- **Video tutorials** for complex features
- **Troubleshooting guides** with common issues

## 🚀 Release Process

### Version Numbering

We follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes or major healthcare feature updates
- **MINOR**: New features and enhancements
- **PATCH**: Bug fixes and security updates

### Release Checklist

- [ ] All tests passing
- [ ] Security scan completed
- [ ] Healthcare compliance verified
- [ ] Arabic language features tested
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

## 🎯 Getting Help

### Community Support

- **GitHub Discussions**: For general questions and feature requests
- **Issues**: For bug reports and technical problems
- **Security**: Use security@brainsait.com for security issues
- **Healthcare**: Contact healthcare@brainsait.com for clinical questions

### Development Support

- **Code Reviews**: Tag @brainsait/core-team for reviews
- **Architecture**: Tag @brainsait/architects for design questions
- **Security**: Tag @brainsait/security for security-related PRs
- **Arabic**: Tag @brainsait/localization for language support

Thank you for contributing to the future of healthcare technology in Saudi Arabia! 🏥✨

---

*This contributing guide is a living document. Please suggest improvements via pull requests.*
