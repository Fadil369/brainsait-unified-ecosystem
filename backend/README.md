# BrainSAIT Healthcare Platform - Backend

## Overview

This is the unified backend implementation for the BrainSAIT Healthcare Unification Platform. It provides a comprehensive healthcare identity management system with OID (Object Identifier) generation, NPHIES integration, and AI analytics capabilities.

## Key Features

- **Unified Healthcare Identity Management**: Centralized registration and management of healthcare entities with secure OID generation.
- **Database Flexibility**: Supports both PostgreSQL and SQLite, with automatic fallback to SQLite if PostgreSQL is unavailable.
- **Enhanced Error Handling**: Comprehensive error handling with detailed feedback.
- **Python Version Compatibility**: Works with Python 3.10+ including Python 3.13.
- **NPHIES Integration**: Ready-to-use integration with the National Platform for Health Insurance Exchange Services.
- **AI Analytics**: Integration point for healthcare data analytics.
- **OID Tree Management**: Hierarchical OID management for healthcare entities.

## Requirements

- Python 3.10+ (including 3.13)
- FastAPI
- Database (PostgreSQL or SQLite)
- Other dependencies listed in `requirements_unified.txt`

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements_unified.txt
```

## Configuration

The application supports configuration via environment variables:

- `DB_TYPE`: Database type to use (either "postgres" or "sqlite", defaults to "sqlite")
- `LOG_LEVEL`: Logging level (defaults to "INFO")
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS (defaults to "\*")

For PostgreSQL:

- `DB_HOST`: PostgreSQL host (defaults to "localhost")
- `DB_PORT`: PostgreSQL port (defaults to "5433")
- `DB_NAME`: PostgreSQL database name (defaults to "nphies_db")
- `DB_USER`: PostgreSQL user (defaults to "nphies_user")
- `DB_PASS`: PostgreSQL password (defaults to "nphies_pass")

## Running the Application

```bash
# Start the application
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Once the application is running, you can access:

- API documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## Database Schema

The application maintains two main tables:

1. `healthcare_identities`: Stores healthcare entities with their OIDs
2. `nphies_claims`: Stores NPHIES claims information

## License

Proprietary - BrainSAIT
