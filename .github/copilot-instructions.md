# BrainSAIT Healthcare Platform - AI Coding Instructions

## Project Overview

This is a **Saudi Arabia-focused healthcare revenue cycle management platform** implementing NPHIES integration, medical coding training, and BOT (Build-Operate-Transfer) business model operations. The system handles sensitive healthcare data with Arabic-first UI design and strict compliance requirements.

## Architecture Patterns

### Unified Monolithic Structure

- **Single Backend App**: `backend/main.py` contains unified FastAPI application (936 lines) with modular endpoints
- **Service Layer**: Domain services in `backend/services/` (nphies, rcm, training, bot, operations, ai_arabic)
- **Frontend**: React + Vite with Arabic RTL support using Material-UI v5 and Emotion CSS-in-JS
- **Database**: PostgreSQL with Arabic text search capabilities and healthcare-specific schemas

### Arabic-First Design Requirements

- **All UI components MUST support RTL layouts** - this is non-negotiable
- Use `stylis-plugin-rtl` for CSS RTL transformation in `vite.config.js`
- Arabic fonts: Noto Sans Arabic, Cairo (configured in theme)
- Test with Arabic sample data from database
- Language switching via `LanguageContext.jsx` with i18next

## Critical Development Commands

### Frontend (React + Vite in `oid-portal/`)

```bash
npm run dev          # Vite dev server on port 5173
npm run build        # Production build
npm run test         # Vitest testing
npm run lint         # ESLint validation
```

### Backend (FastAPI in `backend/`)

```bash
uvicorn main:app --reload --port 8000    # Development server
pytest -v                                # Run tests
pip install -r requirements.txt          # Dependencies
```

### Docker Development

```bash
docker-compose up -d                     # Start all services
docker-compose logs -f                   # View logs
docker-compose exec db psql -U brainsait_admin -d brainsait_healthcare
```

## Key File Patterns

### Backend Service Integration

- Services in `backend/services/` follow pattern: `{domain}_service.py`
- All services imported and used in `main.py` unified endpoints
- Database operations use PostgreSQL with Arabic collation support
- FHIR R4 compliance required for all healthcare data structures

### Frontend Component Architecture

```text
src/
├── contexts/          # State management (Auth, Language, UnifiedHealthcare)
├── components/        # Reusable UI with RTL support
├── pages/            # Route components
├── hooks/            # Custom React hooks
└── services/         # API communication
```

### State Management Pattern

- **React Query**: Server state and caching
- **React Context**: Auth, language, and healthcare state
- **Zustand**: Client-side state (referenced in dependencies)
- **Emotion + RTL**: CSS-in-JS with automatic RTL transformation

## Critical Integration Points

### NPHIES Healthcare Standards

- All patient/provider data must use FHIR R4 format
- NPHIES-specific identifiers and Saudi healthcare codes required
- Implement comprehensive error handling for NPHIES API responses
- `backend/services/nphies_service.py` handles all NPHIES operations

### API Proxy Configuration

Vite proxies all `/api/*` requests to FastAPI backend at `localhost:8000`:

```javascript
// vite.config.js proxy setup
'/api': { target: 'http://localhost:8000', changeOrigin: true }
```

### Database Schema Specifics

- Healthcare tables: `healthcare_identities`, `nphies_claims`, `healthcare_organizations`
- Training platform: `training_programs`, `student_enrollments`
- BOT lifecycle: `bot_projects`, `bot_milestones`
- Arabic text search indexes with proper collation

## Compliance & Security Requirements

### Healthcare Data Protection

- **NEVER expose patient data in logs or error messages**
- Follow PDPL (Saudi Personal Data Protection Law) requirements
- Implement comprehensive audit trails for all data access
- Use proper encryption for data at rest and in transit

### Code Quality Standards

- Run `npm run lint` (frontend) and `pytest` (backend) before commits
- Test Arabic content rendering and RTL layouts
- Validate FHIR compliance with Saudi healthcare sample data
- Comprehensive error handling for NPHIES API integration

## BOT Business Model Context

The platform supports three phases:

1. **BUILD** (Months 1-12): Platform development and setup
2. **OPERATE** (Months 13-36): Full RCM operations delivery
3. **TRANSFER** (Months 37-48): Knowledge transfer to clients

This context affects feature prioritization and architectural decisions around scalability and knowledge transfer capabilities.

## Essential Environment Setup

```bash
# Backend (.env)
DB_HOST=localhost
DB_USER=brainsait_admin
DB_NAME=brainsait_healthcare
OPENAI_API_KEY=your_key
NPHIES_CLIENT_ID=your_nphies_id

# Frontend (.env)
VITE_API_URL=http://localhost:8000
```

## Key References

- `CLAUDE.md`: Comprehensive development guide with commands and architecture details
- `backend/main.py`: Unified API endpoint definitions
- `src/contexts/UnifiedHealthcareContext.jsx`: Central healthcare state management
- `docker-compose.yml`: Complete container orchestration setup
- `src/pages/OidTree.jsx`: Healthcare identity tree visualization component
