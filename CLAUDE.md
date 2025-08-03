# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **BrainSAIT Healthcare Unification Platform** - a comprehensive Saudi Arabia-focused healthcare revenue cycle management system implementing a Build-Operate-Transfer (BOT) business model. The platform integrates NPHIES (National Platform for Health Information Exchange Services), provides medical coding training, and delivers full RCM operations with AI-powered analytics.

**Key Capabilities:**
- NPHIES-native integration for Saudi healthcare compliance
- Medical coding certification programs (CPC, NPHIES, RCMP, HITS)
- Revenue cycle management with 95%+ accuracy standards
- Arabic-first UI with bilingual support (Arabic/English)
- AI-powered claims analysis and duplicate detection
- BOT lifecycle management for healthcare organizations
- 24/7 operations center with real-time monitoring

## Development Commands

### Frontend Development (React + Vite)
```bash
cd oid-portal

# Start development server (port 5173 by default with Vite)
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Run tests with Vitest
npm test
npm run test:ui  # With UI dashboard

# Preview production build
npm run preview
```

### Backend Development (FastAPI + Python)
```bash
cd backend

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --port 8000

# Run tests
pytest
pytest -v  # Verbose output
pytest tests/test_specific.py  # Single test file

# Production server
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker Development
```bash
# Start all services (development)
docker-compose up -d

# View logs
docker-compose logs -f [service_name]

# Rebuild and restart
docker-compose build
docker-compose up -d

# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Database operations
docker-compose exec db psql -U oid_admin -d oid_registry
```

### Database Management
```bash
# Initialize database (runs automatically on first start)
docker-compose exec db psql -U oid_admin -d oid_registry < backend/init.sql

# Connect to database
docker-compose exec db psql -U oid_admin -d oid_registry

# Run migrations (if using Alembic)
cd backend
alembic upgrade head
```

## Architecture Overview

### System Architecture
The platform implements a unified monolithic-first architecture that can scale:

```
brainSAIT-oid-system/
├── backend/              # FastAPI unified API (Python)
│   ├── main.py          # Main application entry point
│   ├── services/        # Business logic services
│   └── config/          # Configuration management
├── oid-portal/          # React frontend with Arabic RTL support
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── contexts/    # React contexts (Auth, Language, Healthcare)
│   │   ├── hooks/       # Custom React hooks
│   │   └── pages/       # Page components
│   └── vite.config.js   # Vite configuration
├── database/            # PostgreSQL with Arabic text search
├── docker-compose.yml   # Development containerization
└── UNIFICATION_SYSTEM.md # Complete platform vision
```

### Backend Architecture (FastAPI)
- **Single Application Pattern**: `main.py` contains the unified API with modular endpoint organization
- **Healthcare Entity Management**: Comprehensive system for patients, providers, organizations
- **NPHIES Integration**: Native Saudi healthcare platform connectivity with FHIR R4 compliance
- **AI Services**: OpenAI integration for claims analysis and Arabic NLP processing
- **Database Layer**: PostgreSQL with specialized healthcare tables and Arabic text indexing
- **Service Layer**: Modular services for different domains (nphies_service.py, rcm_service.py, etc.)

### Frontend Architecture (React)
- **Arabic-First Design**: RTL layouts with Noto Sans Arabic and Cairo fonts
- **Material-UI v5**: Healthcare-appropriate dark theme with BrainSAIT branding
- **State Management**: 
  - React Query for server state and caching
  - Zustand for client state
  - React Context for auth, language, and healthcare context
- **Internationalization**: i18next with Arabic/English switching
- **Routing Structure**:
  - `/` - Unified dashboard
  - `/healthcare` - Provider management
  - `/nphies` - NPHIES claims dashboard  
  - `/rcm` - Revenue cycle management
  - `/ai-analytics` - AI-powered insights
  - `/training` - Medical coding platform
  - `/bot-projects` - BOT lifecycle management
  - `/operations` - 24/7 operations center
  - `/oid-tree` - Healthcare identity tree visualization

### Database Schema
PostgreSQL with healthcare-focused design:
- **Core Tables**: `healthcare_identities`, `nphies_claims`, `healthcare_organizations`
- **Training Platform**: `training_programs`, `student_enrollments`, `training_progress`
- **BOT Lifecycle**: `bot_projects`, `bot_milestones`, `knowledge_transfers`
- **Operations**: `operations_metrics`, `staff_shifts`, `system_alerts`
- **Arabic Support**: Full-text search indexes with Arabic collation
- **Compliance**: Comprehensive audit logging for PDPL/HIPAA requirements

## Key Technologies

### Backend Stack
- **FastAPI 0.104.1**: High-performance async API framework
- **PostgreSQL 14**: Primary database with Arabic text capabilities
- **Redis**: Caching and session management (aioredis 2.0.1)
- **FHIR Libraries**: `hl7 0.4.5`, `fhir.resources 7.0.2` for healthcare standards
- **AI/ML**: OpenAI 1.3.7, Transformers 4.36.2, PyTorch 2.1.1 for analytics
- **Arabic Processing**: `arabic-reshaper 3.0.0`, `python-bidi 0.4.2`, `pyarabic 0.6.15`

### Frontend Stack  
- **React 18.2.0**: Modern hooks-based UI framework
- **Vite 5.0.8**: Build tool with HMR and optimized builds
- **Material-UI 5.15.0**: Component library with Arabic typography support
- **React Query 3.39.3**: Data fetching and caching
- **React Router 6.22.1**: Client-side routing
- **Emotion 11.14.0**: CSS-in-JS with RTL plugin support (stylis-plugin-rtl 2.1.1)
- **i18next 23.7.6**: Internationalization framework

## BOT Business Model Implementation

The platform follows a comprehensive Build-Operate-Transfer approach:

### Phase 1: BUILD (Months 1-12)
- NPHIES-compliant RCM platform development
- AI-powered claims analysis engine
- 24/7 operations centers setup
- Medical coding specialist recruitment (500+ staff)

### Phase 2: OPERATE (Months 13-36)  
- Full RCM operations delivery
- Medical coding certification programs
- Performance metrics: 95%+ claim acceptance, <2% denial rate
- Training delivery: 25,000+ certified professionals

### Phase 3: TRANSFER (Months 37-48)
- Knowledge transfer to client organizations
- Technology platform licensing
- Sustainability measures and local capability building

## Development Guidelines

### Arabic Language Support
- All UI components must support RTL layouts
- Use Arabic fonts (Noto Sans Arabic, Cairo) for Arabic content
- Test with Arabic sample data from the database
- Implement proper text shaping with arabic-reshaper library

### NPHIES Integration
- All healthcare data must comply with FHIR R4 standards
- Use NPHIES-specific identifiers and codes
- Implement proper error handling for NPHIES API responses
- Include Arabic field descriptions in API documentation

### Healthcare Compliance
- Never expose sensitive patient data in logs
- Implement comprehensive audit trails
- Use proper encryption for data at rest and in transit
- Follow PDPL (Saudi Personal Data Protection Law) requirements

### Testing Requirements
- Test Arabic content rendering and RTL layouts
- Validate FHIR compliance with sample Saudi healthcare data
- Run `npm run lint` and `pytest` before committing
- Test NPHIES integration with mock data

## Environment Configuration

### Development Environment Variables
```bash
# Backend (.env file in backend/)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=brainsait_healthcare
DB_USER=brainsait_admin
DB_PASS=brainsait_healthcare_2025!
OPENAI_API_KEY=your_openai_key
NPHIES_CLIENT_ID=your_nphies_client_id
NPHIES_CLIENT_SECRET=your_nphies_secret
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Frontend (.env file in oid-portal/)
VITE_API_URL=http://localhost:8000
```

### API Endpoints Structure
- Base URL: `http://localhost:8000`
- Health Check: `/health`
- API Documentation: `/docs` (Swagger), `/redoc` (ReDoc)
- Main API: `/api/v1/*`
- Healthcare Identities: `/healthcare-identities`
- NPHIES Operations: `/nphies/*`
- Training Platform: `/training/*`
- BOT Management: `/bot-projects/*`

## Important Implementation Notes

1. **Saudi-Specific Focus**: This platform is designed specifically for Saudi Arabia's healthcare ecosystem with NPHIES integration as the core foundation.

2. **BOT Business Model**: The entire system architecture supports the Build-Operate-Transfer approach with clear phase management and knowledge transfer capabilities.

3. **Arabic-First Design**: Every UI component must work seamlessly in Arabic with proper RTL support. This is not optional.

4. **Healthcare Compliance**: The system handles sensitive healthcare data and must maintain strict compliance with Saudi PDPL, international HIPAA, and NPHIES requirements.

5. **Operational Scale**: The platform is designed to handle 25,000+ student enrollments, 180+ healthcare facilities, and process millions of claims annually.

6. **AI Integration**: Claims analysis, duplicate detection, and Arabic NLP processing are core features, not add-ons.

7. **OidTree.jsx Integration**: The OidTree component at `/oid-portal/src/pages/OidTree.jsx` is a critical visualization component for healthcare identities and should be referenced when working with identity management features.

## Key Files and Components

### Backend Core Files
- `backend/main.py`: FastAPI application entry point with unified API endpoints
- `backend/unified_healthcare_service.py`: Core healthcare service integration
- `backend/services/`: Domain-specific services (nphies, rcm, training, bot, operations)

### Frontend Core Components
- `src/contexts/UnifiedHealthcareContext.jsx`: Central healthcare state management
- `src/contexts/LanguageContext.jsx`: Arabic/English language switching
- `src/pages/OidTree.jsx`: Healthcare identity tree visualization
- `src/components/Layout.jsx`: Main application layout with RTL support

### Configuration Files
- `vite.config.js`: Vite build configuration with API proxy setup
- `docker-compose.yml`: Container orchestration for development
- `backend/init.sql`: Database initialization with healthcare tables

The platform represents a comprehensive healthcare technology solution that goes far beyond simple OID management, implementing a complete ecosystem for Saudi healthcare transformation aligned with Vision 2030 objectives.