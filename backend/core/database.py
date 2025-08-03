"""
BrainSAIT Database Utilities - Utility Components
Following OidTree 5-component pattern
"""

import sqlite3
import os
import logging
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "healthcare_platform.db")
DB_TYPE = os.getenv("DB_TYPE", "sqlite")

# PostgreSQL configuration (if enabled)
PG_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "brainsait_healthcare"),
    "user": os.getenv("DB_USER", "brainsait_admin"),
    "password": os.getenv("DB_PASS", "")
}


class DatabaseManager:
    """Unified database manager for SQLite and PostgreSQL"""
    
    def __init__(self):
        self.db_type = DB_TYPE
        self.database_path = DATABASE_PATH
        self.pg_config = PG_CONFIG
    
    def get_connection(self):
        """Get database connection based on configuration"""
        if self.db_type == "postgres":
            try:
                import psycopg2
                import psycopg2.extras
                return psycopg2.connect(**self.pg_config)
            except ImportError:
                logger.warning("psycopg2 not available, falling back to SQLite")
                return sqlite3.connect(self.database_path)
            except Exception as e:
                logger.error(f"PostgreSQL connection failed: {e}, falling back to SQLite")
                return sqlite3.connect(self.database_path)
        else:
            return sqlite3.connect(self.database_path)


@contextmanager
def get_db_connection():
    """Unified context manager for database connections"""
    conn = None
    try:
        if DB_TYPE == "postgres":
            try:
                import psycopg2
                import psycopg2.extras
                conn = psycopg2.connect(**PG_CONFIG)
                conn.autocommit = True
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            except ImportError:
                logger.warning("psycopg2 not available, using SQLite")
                conn = sqlite3.connect(DATABASE_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
        else:
            conn = sqlite3.connect(DATABASE_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        yield conn, cursor
        
    except Exception as e:
        error_type = "PostgreSQL" if DB_TYPE == "postgres" else "SQLite"
        logger.error(f"{error_type} database error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def initialize_database():
    """Initialize database with healthcare tables"""
    try:
        with get_db_connection() as (conn, cursor):
            # Healthcare Identities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS healthcare_identities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_type TEXT NOT NULL,
                    user_id TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    name_ar TEXT,
                    role TEXT NOT NULL,
                    access_level TEXT NOT NULL,
                    national_id TEXT,
                    nphies_id TEXT,
                    organization TEXT,
                    department TEXT,
                    oid TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    metadata TEXT
                )
            """)
            
            # NPHIES Claims table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nphies_claims (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim_id TEXT NOT NULL UNIQUE,
                    patient_nphies_id TEXT NOT NULL,
                    provider_nphies_id TEXT NOT NULL,
                    claim_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'SAR',
                    diagnosis_codes TEXT,
                    procedure_codes TEXT,
                    status TEXT DEFAULT 'submitted',
                    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_date TIMESTAMP,
                    response_data TEXT
                )
            """)
            
            # AI Analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL UNIQUE,
                    entity_id TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    results TEXT NOT NULL,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Communication Log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS communication_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT,
                    communication_type TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    content TEXT,
                    status TEXT DEFAULT 'pending',
                    priority TEXT DEFAULT 'normal',
                    language TEXT DEFAULT 'ar',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent_at TIMESTAMP,
                    delivered_at TIMESTAMP,
                    error_message TEXT
                )
            """)
            
            # Audit Log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    user_id TEXT,
                    resource_type TEXT,
                    resource_id TEXT,
                    metadata TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise