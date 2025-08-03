#!/usr/bin/env python3
"""
BrainSAIT Healthcare Platform - Initialization Script

This script initializes the healthcare platform database and required components.
Run this before starting the application for the first time.
"""

import os
import sys
import logging
import argparse
import sqlite3
import importlib.util

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("init")

def is_package_installed(package_name):
    """Check if a Python package is installed"""
    return importlib.util.find_spec(package_name) is not None

def setup_database(db_type="sqlite", reset=False):
    """Initialize the database with required schema"""
    logger.info(f"Setting up {db_type.upper()} database")

    if db_type == "sqlite":
        # SQLite setup
        db_path = os.path.join(os.path.dirname(__file__), "healthcare_platform.db")

        if reset and os.path.exists(db_path):
            logger.warning(f"Removing existing database at {db_path}")
            os.remove(db_path)

        # Create tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create healthcare_identities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS healthcare_identities (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                name_ar TEXT,
                role TEXT NOT NULL,
                access_level TEXT NOT NULL,
                national_id TEXT,
                nphies_id TEXT,
                organization TEXT,
                department TEXT,
                expires TIMESTAMP NOT NULL,
                full_oid TEXT UNIQUE NOT NULL,
                metadata TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create nphies_claims table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nphies_claims (
                id TEXT PRIMARY KEY,
                claim_id TEXT UNIQUE NOT NULL,
                patient_nphies_id TEXT NOT NULL,
                provider_nphies_id TEXT NOT NULL,
                claim_type TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'SAR',
                diagnosis_codes TEXT,
                procedure_codes TEXT,
                status TEXT DEFAULT 'submitted',
                submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create audit_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                entity_id TEXT,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                success BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_healthcare_entity_type
            ON healthcare_identities(entity_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_healthcare_role
            ON healthcare_identities(role)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_logs_entity
            ON audit_logs(entity_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_logs_action
            ON audit_logs(action)
        """)

        conn.commit()
        conn.close()

        logger.info(f"SQLite database initialized at {db_path}")

    elif db_type == "postgres":
        try:
            import psycopg2
            import psycopg2.extras

            # PostgreSQL setup - assuming environment variables are set
            # or using default test values
            pg_config = {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5433")),
                "dbname": os.getenv("DB_NAME", "nphies_db"),
                "user": os.getenv("DB_USER", "nphies_user"),
                "password": os.getenv("DB_PASS", "nphies_pass")
            }

            conn = psycopg2.connect(**pg_config)
            conn.autocommit = True
            cursor = conn.cursor()

            # Drop tables if reset is True
            if reset:
                logger.warning("Dropping existing tables")
                cursor.execute("DROP TABLE IF EXISTS healthcare_identities CASCADE")
                cursor.execute("DROP TABLE IF EXISTS nphies_claims CASCADE")
                cursor.execute("DROP TABLE IF EXISTS audit_logs CASCADE")

            # Create healthcare_identities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS healthcare_identities (
                    id UUID PRIMARY KEY,
                    entity_type VARCHAR(50) NOT NULL,
                    user_id VARCHAR(100) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    name_ar VARCHAR(255),
                    role VARCHAR(50) NOT NULL,
                    access_level VARCHAR(50) NOT NULL,
                    national_id VARCHAR(100),
                    nphies_id VARCHAR(100),
                    organization VARCHAR(255),
                    department VARCHAR(255),
                    expires TIMESTAMP NOT NULL,
                    full_oid VARCHAR(100) UNIQUE NOT NULL,
                    metadata JSONB,
                    status VARCHAR(50) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create nphies_claims table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nphies_claims (
                    id UUID PRIMARY KEY,
                    claim_id VARCHAR(100) UNIQUE NOT NULL,
                    patient_nphies_id VARCHAR(100) NOT NULL,
                    provider_nphies_id VARCHAR(100) NOT NULL,
                    claim_type VARCHAR(100) NOT NULL,
                    amount DECIMAL NOT NULL,
                    currency VARCHAR(3) DEFAULT 'SAR',
                    diagnosis_codes JSONB,
                    procedure_codes JSONB,
                    status VARCHAR(50) DEFAULT 'submitted',
                    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create audit_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id UUID PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    entity_id UUID,
                    action VARCHAR(100) NOT NULL,
                    details TEXT,
                    ip_address VARCHAR(50),
                    user_agent VARCHAR(255),
                    success BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_healthcare_entity_type
                ON healthcare_identities(entity_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_healthcare_role
                ON healthcare_identities(role)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_logs_entity
                ON audit_logs(entity_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_logs_action
                ON audit_logs(action)
            """)

            conn.close()
            logger.info("PostgreSQL database initialized")

        except ImportError:
            logger.error("psycopg2 not installed. Cannot initialize PostgreSQL database.")
            logger.info("Installing PostgreSQL dependencies...")
            logger.info("Run: pip install psycopg2-binary")
            return False
        except Exception as e:
            logger.error(f"PostgreSQL setup failed: {e}")
            return False
    else:
        logger.error(f"Unsupported database type: {db_type}")
        return False

    return True

def check_dependencies():
    """Check for required dependencies"""
    logger.info("Checking dependencies")

    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-dotenv"
    ]

    all_installed = True
    for package in required_packages:
        if not is_package_installed(package):
            logger.error(f"Required package '{package}' is not installed")
            all_installed = False

    # Check optional dependencies
    optional_packages = [
        ("psycopg2", "PostgreSQL support"),
        ("redis", "Redis caching"),
        ("sqlalchemy", "ORM support"),
        ("fhirclient", "FHIR support")
    ]

    for package, description in optional_packages:
        if not is_package_installed(package):
            logger.warning(f"Optional package '{package}' for {description} is not installed")

    return all_installed

def create_dotenv_file():
    """Create a default .env file if it doesn't exist"""
    env_path = os.path.join(os.path.dirname(__file__), ".env")

    if os.path.exists(env_path):
        logger.info(".env file already exists, skipping creation")
        return

    logger.info("Creating default .env file")

    with open(env_path, "w") as f:
        f.write("""# BrainSAIT Healthcare Platform Environment Configuration
# Database settings
DB_TYPE=sqlite  # 'sqlite' or 'postgres'

# PostgreSQL settings (used only if DB_TYPE=postgres)
DB_HOST=localhost
DB_PORT=5433
DB_NAME=nphies_db
DB_USER=nphies_user
DB_PASS=nphies_pass

# Application settings
LOG_LEVEL=INFO
ALLOWED_ORIGINS=*

# Redis settings (optional)
REDIS_ENABLED=false
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Security
JWT_SECRET=changeme_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
""")

    logger.info(f"Default .env file created at {env_path}")
    logger.warning("Make sure to change default values in production!")

def main():
    """Main initialization function"""
    parser = argparse.ArgumentParser(
        description="Initialize the BrainSAIT Healthcare Platform"
    )
    parser.add_argument(
        "--db-type",
        choices=["sqlite", "postgres"],
        default="sqlite",
        help="Database type to initialize"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset existing database"
    )

    args = parser.parse_args()

    logger.info("Starting BrainSAIT Healthcare Platform initialization")

    # Check dependencies
    if not check_dependencies():
        logger.error("Missing required dependencies. Please install them and try again.")
        logger.info("Tip: Run 'pip install -r requirements_unified.txt'")
        return 1

    # Create default .env file
    create_dotenv_file()

    # Set up database
    if not setup_database(args.db_type, args.reset):
        logger.error("Database setup failed")
        return 1

    logger.info("Initialization complete!")
    logger.info("You can now start the application with: uvicorn main:app --reload")

    return 0

if __name__ == "__main__":
    sys.exit(main())
