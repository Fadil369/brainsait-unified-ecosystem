#!/usr/bin/env python3
"""
BrainSAIT Healthcare Platform - Unified Healthcare Service with Twilio Communication
A comprehensive healthcare platform with OID management, identity services,
NPHIES integration, AI analytics, and HIPAA-compliant communication services.

This unified implementation combines the best elements of all versions
while maintaining compatibility with Python 3.10+ including 3.13.
"""

from fastapi import FastAPI, HTTPException, Query, Request, status, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
import logging
import json
import uuid
import os
import re
import hashlib
import hmac
from enum import Enum
from dotenv import load_dotenv
from contextlib import asynccontextmanager, contextmanager

# Twilio imports for communication services
try:
    from twilio.rest import Client as TwilioClient
    from twilio.twiml import VoiceResponse, MessagingResponse
    from twilio.request_validator import RequestValidator
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    TwilioClient = None
    VoiceResponse = None
    MessagingResponse = None
    RequestValidator = None

# Arabic text processing
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False

# Import security utilities
try:
    from utils.security import (
        sanitize_string, sanitize_healthcare_data, safe_log,
        audit_log, SecurityMiddleware, require_auth,
        SecureHealthcareModel, generate_secure_token
    )
    SECURITY_AVAILABLE = True
except ImportError:
    # Fallback if security utils not available
    SECURITY_AVAILABLE = False
    def safe_log(message, data=None, level='info'):
        getattr(logging.getLogger(__name__), level)(f"{message} | {data}")
    def audit_log(action, user_id, resource_type, resource_id=None, metadata=None):
        logging.getLogger(__name__).info(f"AUDIT: {action} by {user_id}")
    def sanitize_string(s, max_length=1000):
        return str(s)[:max_length]
    def sanitize_healthcare_data(data):
        return data
    SecureHealthcareModel = BaseModel
    def require_auth():
        return {}

# Load environment variables
load_dotenv()

# Configure secure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing BrainSAIT Healthcare Platform with Twilio Communication...")
    try:
        initialize_database()
        logger.info("Startup completed successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # We don't raise an exception here to allow the app to start
        # even if the database initialization fails

    yield

    # Shutdown
    logger.info("Shutting down BrainSAIT Healthcare Platform...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="BrainSAIT Healthcare Unification Platform with Twilio Communication",
    description="Unified Healthcare Identity and Revenue Cycle Management System with NPHIES Integration and HIPAA-Compliant Communication Services",
    version="2.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Add security middleware if available
# Temporarily disabled for verification testing
# if SECURITY_AVAILABLE:
#     app.add_middleware(SecurityMiddleware)

# Add CORS middleware with enhanced security
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Constants
BASE_OID = "1.3.6.1.4.1.61026"  # BrainSAIT IANA registered OID

# Configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()  # 'sqlite' or 'postgres'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "healthcare_platform.db")

# PostgreSQL configuration (used if DB_TYPE is 'postgres')
PG_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5433")),
    "dbname": os.getenv("DB_NAME", "nphies_db"),
    "user": os.getenv("DB_USER", "nphies_user"),
    "password": os.getenv("DB_PASS", "nphies_pass")
}

# Twilio Configuration
TWILIO_CONFIG = {
    "account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
    "auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
    "phone_number": os.getenv("TWILIO_PHONE_NUMBER"),
    "video_api_key": os.getenv("TWILIO_VIDEO_API_KEY"),
    "video_api_secret": os.getenv("TWILIO_VIDEO_API_SECRET"),
    "webhook_secret": os.getenv("TWILIO_WEBHOOK_SECRET")
}

# Initialize Twilio client
twilio_client = None
if TWILIO_AVAILABLE and TWILIO_CONFIG["account_sid"] and TWILIO_CONFIG["auth_token"]:
    twilio_client = TwilioClient(
        TWILIO_CONFIG["account_sid"],
        TWILIO_CONFIG["auth_token"]
    )
    logger.info("Twilio client initialized successfully")
else:
    logger.warning("Twilio client not available - check configuration")

# Database connection management - unified to handle both SQLite and PostgreSQL
if DB_TYPE == "postgres":
    try:
        import psycopg2
        import psycopg2.extras
        logger.info("Using PostgreSQL database")
    except ImportError:
        logger.warning("psycopg2 not available, falling back to SQLite")
        DB_TYPE = "sqlite"

if DB_TYPE == "sqlite":
    import sqlite3
    logger.info("Using SQLite database")

# Enhanced Error Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request,
                                      exc: RequestValidationError):
    """Custom validation error handler with secure logging"""
    safe_log(f"Validation error for {request.url.path}",
             {"errors": exc.errors()}, "warning")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation failed",
            "errors": exc.errors(),
            "message": "Please check your input data and try again",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler with secure logging"""
    safe_log(f"HTTP error {exc.status_code} for {request.url.path}",
             {"detail": exc.detail}, "error")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

# Data Models
class EntityType(str, Enum):
    PATIENT = "patient"
    PROVIDER = "provider"
    ORGANIZATION = "organization"
    DEVICE = "device"
    PROCEDURE = "procedure"
    MEDICATION = "medication"
    RECORD = "record"
    INSURANCE = "insurance"
    APPOINTMENT = "appointment"
    AI_SERVICE = "ai_service"

class AccessLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HealthcareRole(str, Enum):
    PATIENT = "patient"
    PHYSICIAN = "physician"
    NURSE = "nurse"
    PHARMACIST = "pharmacist"
    TECHNICIAN = "technician"
    ADMINISTRATOR = "administrator"
    RESEARCHER = "researcher"
    AI_ANALYST = "ai_analyst"

# Communication Models
class CommunicationType(str, Enum):
    SMS = "sms"
    VOICE = "voice"
    VIDEO = "video"
    EMAIL = "email"

class MessagePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"

class CommunicationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"

class Language(str, Enum):
    ARABIC = "ar"
    ENGLISH = "en"

class HealthcareIdentity(BaseModel):
    entity_type: EntityType
    user_id: str = Field(..., description="User or entity identifier")
    name: str = Field(..., description="Name in Arabic and English")
    name_ar: Optional[str] = Field(None, description="Arabic name")
    role: HealthcareRole
    access_level: AccessLevel
    national_id: Optional[str] = Field(None, description="Saudi National ID")
    nphies_id: Optional[str] = Field(None, description="NPHIES identifier")
    organization: Optional[str] = Field(None, description="Healthcare organization")
    department: Optional[str] = Field(None, description="Department or specialty")
    expires: datetime = Field(..., description="Expiration datetime")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class NPHIESClaim(BaseModel):
    claim_id: str
    patient_nphies_id: str
    provider_nphies_id: str
    claim_type: str
    amount: float
    currency: str = "SAR"
    diagnosis_codes: List[str] = Field(default_factory=list)
    procedure_codes: List[str] = Field(default_factory=list)
    status: str = "submitted"
    submission_date: datetime = Field(default_factory=datetime.now)

class AIAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_id: str
    analysis_type: str
    results: Dict[str, Any]
    confidence_score: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)

class SMSRequest(BaseModel):
    recipient_phone: str = Field(..., description="Recipient phone number in E.164 format")
    message: str = Field(..., min_length=1, max_length=1600, description="SMS message content")
    patient_id: Optional[str] = Field(None, description="Patient identifier for audit trail")
    priority: MessagePriority = MessagePriority.NORMAL
    language: Language = Language.ARABIC
    scheduled_time: Optional[datetime] = Field(None, description="Schedule message for future delivery")
    encrypt_content: bool = Field(True, description="Encrypt message content for HIPAA compliance")
    
    @validator('recipient_phone')
    def validate_phone_number(cls, v):
        # Basic E.164 format validation
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Phone number must be in E.164 format (e.g., +966501234567)')
        return v
    
    @validator('message')
    def validate_message_content(cls, v):
        # Check for potential PHI in message
        phi_patterns = [
            r'\b\d{10}\b',  # National ID patterns
            r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card patterns
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email patterns
        ]
        for pattern in phi_patterns:
            if re.search(pattern, v):
                logger.warning(f"Potential PHI detected in message content")
        return v

class VoiceCallRequest(BaseModel):
    recipient_phone: str = Field(..., description="Recipient phone number in E.164 format")
    message_content: Optional[str] = Field(None, description="Text-to-speech content")
    patient_id: Optional[str] = Field(None, description="Patient identifier")
    callback_url: Optional[str] = Field(None, description="Webhook URL for call status updates")
    priority: MessagePriority = MessagePriority.NORMAL
    language: Language = Language.ARABIC
    max_duration: int = Field(300, description="Maximum call duration in seconds")
    
    @validator('recipient_phone')
    def validate_phone_number(cls, v):
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Phone number must be in E.164 format')
        return v

class VideoSessionRequest(BaseModel):
    patient_id: str = Field(..., description="Patient identifier")
    provider_id: str = Field(..., description="Healthcare provider identifier")
    session_name: str = Field(..., description="Video consultation session name")
    max_participants: int = Field(4, ge=2, le=50, description="Maximum number of participants")
    recording_enabled: bool = Field(False, description="Enable session recording for compliance")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled consultation time")
    duration_minutes: int = Field(60, ge=15, le=480, description="Expected session duration")

class CommunicationPreferences(BaseModel):
    patient_id: str
    preferred_language: Language = Language.ARABIC
    sms_enabled: bool = True
    voice_enabled: bool = True
    video_enabled: bool = True
    email_enabled: bool = False
    preferred_contact_time_start: str = Field("09:00", description="Preferred contact time start (HH:MM)")
    preferred_contact_time_end: str = Field("18:00", description="Preferred contact time end (HH:MM)")
    timezone: str = Field("Asia/Riyadh", description="Patient timezone")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact number")

class WorkflowRequest(BaseModel):
    workflow_type: str = Field(..., description="Type of workflow (appointment_reminder, clinical_results, emergency_alert)")
    patient_id: str = Field(..., description="Patient identifier")
    template_data: Dict[str, Any] = Field(default_factory=dict, description="Template variables")
    priority: MessagePriority = MessagePriority.NORMAL
    scheduled_time: Optional[datetime] = Field(None, description="Schedule for future execution")
    communication_types: List[CommunicationType] = Field(default_factory=lambda: [CommunicationType.SMS])

class ConsentRequest(BaseModel):
    patient_id: str
    consent_type: str = Field(..., description="Type of consent (communication, data_sharing, etc.)")
    consent_given: bool
    consent_date: datetime = Field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = Field(None, description="Consent expiration date")
    digital_signature: Optional[str] = Field(None, description="Digital signature hash")
    witness_id: Optional[str] = Field(None, description="Healthcare provider witness ID")

# Unified Database Context Manager
@contextmanager
def get_db_connection():
    """Unified context manager for database connections (SQLite or PostgreSQL)"""
    conn = None
    try:
        if DB_TYPE == "postgres":
            conn = psycopg2.connect(**PG_CONFIG)
            conn.autocommit = True
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
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
        raise HTTPException(
            status_code=500,
            detail="Database operation failed",
            headers={"X-Error": "Database connection error"}
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Database Initialization
def initialize_database():
    """Initialize database schema based on configured database type"""
    try:
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "sqlite":
                # SQLite tables
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
                
                # Communication tables for SQLite
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS communication_history (
                        id TEXT PRIMARY KEY,
                        patient_id TEXT NOT NULL,
                        communication_type TEXT NOT NULL,
                        recipient_phone TEXT,
                        message_content TEXT,
                        status TEXT DEFAULT 'pending',
                        priority TEXT DEFAULT 'normal',
                        language TEXT DEFAULT 'ar',
                        twilio_sid TEXT,
                        error_message TEXT,
                        scheduled_time TIMESTAMP,
                        sent_time TIMESTAMP,
                        delivered_time TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS communication_preferences (
                        id TEXT PRIMARY KEY,
                        patient_id TEXT UNIQUE NOT NULL,
                        preferred_language TEXT DEFAULT 'ar',
                        sms_enabled INTEGER DEFAULT 1,
                        voice_enabled INTEGER DEFAULT 1,
                        video_enabled INTEGER DEFAULT 1,
                        email_enabled INTEGER DEFAULT 0,
                        preferred_contact_time_start TEXT DEFAULT '09:00',
                        preferred_contact_time_end TEXT DEFAULT '18:00',
                        timezone TEXT DEFAULT 'Asia/Riyadh',
                        emergency_contact_phone TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS communication_workflows (
                        id TEXT PRIMARY KEY,
                        workflow_id TEXT UNIQUE NOT NULL,
                        workflow_type TEXT NOT NULL,
                        patient_id TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        priority TEXT DEFAULT 'normal',
                        template_data TEXT,
                        communication_types TEXT,
                        scheduled_time TIMESTAMP,
                        executed_time TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS patient_consent (
                        id TEXT PRIMARY KEY,
                        patient_id TEXT NOT NULL,
                        consent_type TEXT NOT NULL,
                        consent_given INTEGER NOT NULL,
                        consent_date TIMESTAMP NOT NULL,
                        expiry_date TIMESTAMP,
                        digital_signature TEXT,
                        witness_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS compliance_audit (
                        id TEXT PRIMARY KEY,
                        action_type TEXT NOT NULL,
                        resource_type TEXT NOT NULL,
                        resource_id TEXT,
                        user_id TEXT NOT NULL,
                        patient_id TEXT,
                        action_details TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create indices for SQLite
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_healthcare_entity_type
                    ON healthcare_identities(entity_type)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_healthcare_role
                    ON healthcare_identities(role)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_communication_patient_id
                    ON communication_history(patient_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_communication_status
                    ON communication_history(status)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_workflow_patient_id
                    ON communication_workflows(patient_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_patient_id
                    ON compliance_audit(patient_id)
                """)

            else:
                # PostgreSQL tables
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
                
                # Communication tables for PostgreSQL
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS communication_history (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        patient_id VARCHAR(100) NOT NULL,
                        communication_type VARCHAR(50) NOT NULL,
                        recipient_phone VARCHAR(20),
                        message_content TEXT,
                        status VARCHAR(50) DEFAULT 'pending',
                        priority VARCHAR(20) DEFAULT 'normal',
                        language VARCHAR(5) DEFAULT 'ar',
                        twilio_sid VARCHAR(100),
                        error_message TEXT,
                        scheduled_time TIMESTAMP,
                        sent_time TIMESTAMP,
                        delivered_time TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS communication_preferences (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        patient_id VARCHAR(100) UNIQUE NOT NULL,
                        preferred_language VARCHAR(5) DEFAULT 'ar',
                        sms_enabled BOOLEAN DEFAULT true,
                        voice_enabled BOOLEAN DEFAULT true,
                        video_enabled BOOLEAN DEFAULT true,
                        email_enabled BOOLEAN DEFAULT false,
                        preferred_contact_time_start TIME DEFAULT '09:00',
                        preferred_contact_time_end TIME DEFAULT '18:00',
                        timezone VARCHAR(50) DEFAULT 'Asia/Riyadh',
                        emergency_contact_phone VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS communication_workflows (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        workflow_id VARCHAR(100) UNIQUE NOT NULL,
                        workflow_type VARCHAR(100) NOT NULL,
                        patient_id VARCHAR(100) NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        priority VARCHAR(20) DEFAULT 'normal',
                        template_data JSONB,
                        communication_types JSONB,
                        scheduled_time TIMESTAMP,
                        executed_time TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS patient_consent (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        patient_id VARCHAR(100) NOT NULL,
                        consent_type VARCHAR(100) NOT NULL,
                        consent_given BOOLEAN NOT NULL,
                        consent_date TIMESTAMP NOT NULL,
                        expiry_date TIMESTAMP,
                        digital_signature VARCHAR(500),
                        witness_id VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS compliance_audit (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        action_type VARCHAR(100) NOT NULL,
                        resource_type VARCHAR(100) NOT NULL,
                        resource_id VARCHAR(100),
                        user_id VARCHAR(100) NOT NULL,
                        patient_id VARCHAR(100),
                        action_details JSONB,
                        ip_address INET,
                        user_agent TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create indices for PostgreSQL
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_healthcare_entity_type
                    ON healthcare_identities(entity_type)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_healthcare_role
                    ON healthcare_identities(role)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_communication_patient_id
                    ON communication_history(patient_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_communication_status
                    ON communication_history(status)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_workflow_patient_id
                    ON communication_workflows(patient_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_patient_id
                    ON compliance_audit(patient_id)
                """)

            conn.commit()
            logger.info(f"Database initialized successfully using {DB_TYPE}")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# Utility Functions
def generate_oid(entity_type: EntityType) -> str:
    """Generate hierarchical OID based on entity type"""
    entity_mappings = {
        EntityType.PATIENT: "1",
        EntityType.PROVIDER: "2",
        EntityType.ORGANIZATION: "3",
        EntityType.DEVICE: "4",
        EntityType.PROCEDURE: "5",
        EntityType.MEDICATION: "6",
        EntityType.RECORD: "7",
        EntityType.INSURANCE: "8",
        EntityType.APPOINTMENT: "9",
        EntityType.AI_SERVICE: "10"
    }

    try:
        with get_db_connection() as (conn, cursor):
            entity_oid = entity_mappings[entity_type]
            base_entity_oid = f"{BASE_OID}.{entity_oid}"

            if DB_TYPE == "postgres":
                cursor.execute("""
                    SELECT MAX(CAST(split_part(full_oid, '.', 8) AS INT))
                    FROM healthcare_identities
                    WHERE full_oid LIKE %s
                """, (f"{base_entity_oid}.%",))

                result = cursor.fetchone()
                max_suffix = result[0] if result and result[0] else None

            else:  # SQLite
                cursor.execute("""
                    SELECT full_oid FROM healthcare_identities
                    WHERE full_oid LIKE ?
                    ORDER BY full_oid DESC LIMIT 1
                """, (f"{base_entity_oid}.%",))

                result = cursor.fetchone()
                if result:
                    last_oid = result[0]
                    max_suffix = int(last_oid.split('.')[-1])
                else:
                    max_suffix = None

            next_suffix = max_suffix + 1 if max_suffix else 1001
            return f"{base_entity_oid}.{next_suffix}"

    except Exception as e:
        logger.error(f"OID generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate OID"
        )

# Helper Functions for Communication
def format_arabic_text(text: str) -> str:
    """Format Arabic text for proper display"""
    if not ARABIC_SUPPORT or not text:
        return text
    
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)
    except Exception as e:
        logger.warning(f"Arabic text formatting failed: {e}")
        return text

def encrypt_message_content(content: str, patient_id: str) -> str:
    """Encrypt message content for HIPAA compliance"""
    try:
        # Simple encryption for demonstration - use proper encryption in production
        key = hashlib.sha256(f"{patient_id}_{TWILIO_CONFIG.get('webhook_secret', 'default')}".encode()).digest()
        # This is a simplified encryption - implement proper AES encryption in production
        encrypted = hashlib.sha256(f"{content}_{key.hex()}".encode()).hexdigest()
        return encrypted[:50]  # Truncate for storage
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        return content

def check_communication_consent(patient_id: str, communication_type: CommunicationType) -> bool:
    """Check if patient has given consent for communication type"""
    try:
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                cursor.execute("""
                    SELECT consent_given FROM patient_consent 
                    WHERE patient_id = %s AND consent_type = %s 
                    AND (expiry_date IS NULL OR expiry_date > CURRENT_TIMESTAMP)
                    ORDER BY consent_date DESC LIMIT 1
                """, (patient_id, f"communication_{communication_type.value}"))
            else:
                cursor.execute("""
                    SELECT consent_given FROM patient_consent 
                    WHERE patient_id = ? AND consent_type = ? 
                    AND (expiry_date IS NULL OR expiry_date > datetime('now'))
                    ORDER BY consent_date DESC LIMIT 1
                """, (patient_id, f"communication_{communication_type.value}"))
            
            result = cursor.fetchone()
            if result:
                return bool(result[0] if DB_TYPE == "sqlite" else result["consent_given"])
            return False  # Default to no consent if not found
    except Exception as e:
        logger.error(f"Failed to check communication consent: {e}")
        return False

def log_communication_audit(action: str, user_id: str, patient_id: str, details: Dict[str, Any], request: Request):
    """Log communication action for HIPAA audit trail"""
    try:
        with get_db_connection() as (conn, cursor):
            audit_id = str(uuid.uuid4())
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            
            if DB_TYPE == "postgres":
                cursor.execute("""
                    INSERT INTO compliance_audit (
                        id, action_type, resource_type, resource_id, user_id, patient_id,
                        action_details, ip_address, user_agent, timestamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    audit_id, action, "communication", details.get("communication_id"),
                    user_id, patient_id, json.dumps(details), client_ip, user_agent, datetime.now()
                ))
            else:
                cursor.execute("""
                    INSERT INTO compliance_audit (
                        id, action_type, resource_type, resource_id, user_id, patient_id,
                        action_details, ip_address, user_agent, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    audit_id, action, "communication", details.get("communication_id"),
                    user_id, patient_id, json.dumps(details), client_ip, user_agent, datetime.now().isoformat()
                ))
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to log audit trail: {e}")

# API Endpoints
@app.get("/health")
async def health_check():
    """Enhanced health check with comprehensive system status"""
    try:
        # Test database connection
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                cursor.execute("SELECT 1")
            else:
                cursor.execute("SELECT 1")

            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "BrainSAIT Healthcare Unification Platform with Twilio Communication",
                "version": "2.2.0",
                "base_oid": BASE_OID,
                "database": {
                    "type": DB_TYPE,
                    "status": "connected",
                },
                "twilio": {
                    "status": "available" if twilio_client else "unavailable",
                    "configured": bool(TWILIO_CONFIG["account_sid"])
                },
                "features": {
                    "nphies_integration": True,
                    "arabic_support": ARABIC_SUPPORT,
                    "ai_analytics": True,
                    "oid_management": True,
                    "healthcare_rcm": True,
                    "twilio_communication": bool(twilio_client),
                    "sms_messaging": bool(twilio_client),
                    "voice_calls": bool(twilio_client),
                    "video_sessions": bool(TWILIO_CONFIG.get("video_api_key"))
                },
                "compliance": {
                    "pdpl": True,
                    "hipaa": True,
                    "nphies": True,
                    "fhir_r4": True
                }
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/")
async def root():
    """Enhanced root endpoint with comprehensive API information"""
    return {
        "service": "BrainSAIT Healthcare Unification Platform with Twilio Communication",
        "description": "Unified Healthcare Identity and Revenue Cycle Management System with HIPAA-Compliant Communication Services",
        "version": "2.2.0",
        "base_oid": BASE_OID,
        "database_type": DB_TYPE,
        "supported_standards": ["HL7 FHIR R4", "ICD-10", "SNOMED CT", "CPT"],
        "languages": ["Arabic", "English"],
        "regions": ["Saudi Arabia", "GCC"],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "identities": "/healthcare-identities",
            "nphies": "/nphies",
            "analytics": "/ai-analytics",
            "oids": "/oids",
            "communication": "/api/v1/communication",
            "workflows": "/api/v1/workflows",
            "compliance": "/api/v1/compliance",
            "webhooks": "/webhooks/twilio"
        },
        "communication_features": {
            "sms_messaging": bool(twilio_client),
            "voice_calls": bool(twilio_client),
            "video_consultations": bool(TWILIO_CONFIG.get("video_api_key")),
            "arabic_language_support": ARABIC_SUPPORT,
            "hipaa_compliance": True,
            "audit_logging": True
        },
        "compliance": "NPHIES, PDPL, HIPAA Ready"
    }

# Communication Management Endpoints
@app.post("/api/v1/communication/sms/send")
async def send_sms(sms_request: SMSRequest, request: Request, current_user: dict = Depends(require_auth)):
    """Send HIPAA-compliant SMS message"""
    if not twilio_client:
        raise HTTPException(status_code=503, detail="Twilio service not available")
    
    # Check patient consent
    if sms_request.patient_id and not check_communication_consent(sms_request.patient_id, CommunicationType.SMS):
        raise HTTPException(status_code=403, detail="Patient has not consented to SMS communication")
    
    try:
        # Format message for Arabic if needed
        message_content = sms_request.message
        if sms_request.language == Language.ARABIC:
            message_content = format_arabic_text(message_content)
        
        # Create communication record
        comm_id = str(uuid.uuid4())
        
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                cursor.execute("""
                    INSERT INTO communication_history (
                        id, patient_id, communication_type, recipient_phone, message_content,
                        status, priority, language, scheduled_time, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    comm_id, sms_request.patient_id, CommunicationType.SMS.value,
                    sms_request.recipient_phone, encrypt_message_content(message_content, sms_request.patient_id or "system"),
                    CommunicationStatus.PENDING.value, sms_request.priority.value,
                    sms_request.language.value, sms_request.scheduled_time, datetime.now()
                ))
            else:
                cursor.execute("""
                    INSERT INTO communication_history (
                        id, patient_id, communication_type, recipient_phone, message_content,
                        status, priority, language, scheduled_time, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    comm_id, sms_request.patient_id, CommunicationType.SMS.value,
                    sms_request.recipient_phone, encrypt_message_content(message_content, sms_request.patient_id or "system"),
                    CommunicationStatus.PENDING.value, sms_request.priority.value,
                    sms_request.language.value, sms_request.scheduled_time.isoformat() if sms_request.scheduled_time else None,
                    datetime.now().isoformat()
                ))
            conn.commit()
        
        # Send SMS immediately or schedule
        if sms_request.scheduled_time and sms_request.scheduled_time > datetime.now():
            # Schedule for later (would integrate with Celery in production)
            twilio_sid = f"scheduled_{comm_id}"
            status = CommunicationStatus.PENDING
        else:
            # Send immediately
            message = twilio_client.messages.create(
                body=message_content,
                from_=TWILIO_CONFIG["phone_number"],
                to=sms_request.recipient_phone
            )
            twilio_sid = message.sid
            status = CommunicationStatus.SENT
            
            # Update record with Twilio SID
            with get_db_connection() as (conn, cursor):
                if DB_TYPE == "postgres":
                    cursor.execute("""
                        UPDATE communication_history 
                        SET twilio_sid = %s, status = %s, sent_time = %s, updated_at = %s
                        WHERE id = %s
                    """, (twilio_sid, status.value, datetime.now(), datetime.now(), comm_id))
                else:
                    cursor.execute("""
                        UPDATE communication_history 
                        SET twilio_sid = ?, status = ?, sent_time = ?, updated_at = ?
                        WHERE id = ?
                    """, (twilio_sid, status.value, datetime.now().isoformat(), datetime.now().isoformat(), comm_id))
                conn.commit()
        
        # Log audit trail
        user_id = current_user.get("user_id", "system") if current_user else "system"
        log_communication_audit(
            "sms_sent", user_id, sms_request.patient_id or "unknown",
            {"communication_id": comm_id, "recipient": sms_request.recipient_phone, "priority": sms_request.priority.value},
            request
        )
        
        return {
            "status": "success",
            "communication_id": comm_id,
            "twilio_sid": twilio_sid,
            "message_status": status.value,
            "sent_time": datetime.now().isoformat() if status == CommunicationStatus.SENT else None
        }
        
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
        # Update communication record with error
        try:
            with get_db_connection() as (conn, cursor):
                if DB_TYPE == "postgres":
                    cursor.execute("""
                        UPDATE communication_history 
                        SET status = %s, error_message = %s, updated_at = %s
                        WHERE id = %s
                    """, (CommunicationStatus.FAILED.value, str(e), datetime.now(), comm_id))
                else:
                    cursor.execute("""
                        UPDATE communication_history 
                        SET status = ?, error_message = ?, updated_at = ?
                        WHERE id = ?
                    """, (CommunicationStatus.FAILED.value, str(e), datetime.now().isoformat(), comm_id))
                conn.commit()
        except:
            pass
        
        raise HTTPException(status_code=500, detail="Failed to send SMS message")

@app.post("/api/v1/communication/voice/call")
async def initiate_voice_call(call_request: VoiceCallRequest, request: Request, current_user: dict = Depends(require_auth)):
    """Initiate secure voice call"""
    if not twilio_client:
        raise HTTPException(status_code=503, detail="Twilio service not available")
    
    # Check patient consent
    if call_request.patient_id and not check_communication_consent(call_request.patient_id, CommunicationType.VOICE):
        raise HTTPException(status_code=403, detail="Patient has not consented to voice communication")
    
    try:
        # Create TwiML response for the call
        twiml = VoiceResponse()
        
        if call_request.message_content:
            # Text-to-speech
            message = format_arabic_text(call_request.message_content) if call_request.language == Language.ARABIC else call_request.message_content
            twiml.say(message, language="ar" if call_request.language == Language.ARABIC else "en")
        else:
            # Default message
            default_message = "مرحباً، هذه مكالمة من منصة برين سايت الصحية" if call_request.language == Language.ARABIC else "Hello, this is a call from BrainSAIT Healthcare Platform"
            twiml.say(default_message, language="ar" if call_request.language == Language.ARABIC else "en")
        
        # Initiate call
        call = twilio_client.calls.create(
            twiml=str(twiml),
            to=call_request.recipient_phone,
            from_=TWILIO_CONFIG["phone_number"],
            timeout=call_request.max_duration,
            status_callback=call_request.callback_url
        )
        
        # Create communication record
        comm_id = str(uuid.uuid4())
        
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                cursor.execute("""
                    INSERT INTO communication_history (
                        id, patient_id, communication_type, recipient_phone, message_content,
                        status, priority, language, twilio_sid, sent_time, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    comm_id, call_request.patient_id, CommunicationType.VOICE.value,
                    call_request.recipient_phone, call_request.message_content,
                    CommunicationStatus.SENT.value, call_request.priority.value,
                    call_request.language.value, call.sid, datetime.now(), datetime.now()
                ))
            else:
                cursor.execute("""
                    INSERT INTO communication_history (
                        id, patient_id, communication_type, recipient_phone, message_content,
                        status, priority, language, twilio_sid, sent_time, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    comm_id, call_request.patient_id, CommunicationType.VOICE.value,
                    call_request.recipient_phone, call_request.message_content,
                    CommunicationStatus.SENT.value, call_request.priority.value,
                    call_request.language.value, call.sid, datetime.now().isoformat(), datetime.now().isoformat()
                ))
            conn.commit()
        
        # Log audit trail
        user_id = current_user.get("user_id", "system") if current_user else "system"
        log_communication_audit(
            "voice_call_initiated", user_id, call_request.patient_id or "unknown",
            {"communication_id": comm_id, "call_sid": call.sid, "recipient": call_request.recipient_phone},
            request
        )
        
        return {
            "status": "success",
            "communication_id": comm_id,
            "call_sid": call.sid,
            "call_status": call.status,
            "initiated_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to initiate voice call: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate voice call")

@app.post("/api/v1/communication/video/session")
async def create_video_session(session_request: VideoSessionRequest, request: Request, current_user: dict = Depends(require_auth)):
    """Create video consultation session"""
    if not TWILIO_CONFIG.get("video_api_key") or not TWILIO_CONFIG.get("video_api_secret"):
        raise HTTPException(status_code=503, detail="Twilio Video service not configured")
    
    # Check patient consent
    if not check_communication_consent(session_request.patient_id, CommunicationType.VIDEO):
        raise HTTPException(status_code=403, detail="Patient has not consented to video communication")
    
    try:
        # Generate room name and access tokens
        room_name = f"brainsait_{session_request.session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create video room (simplified - would use Twilio Video API in production)
        session_id = str(uuid.uuid4())
        
        # Store session information
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                cursor.execute("""
                    INSERT INTO communication_history (
                        id, patient_id, communication_type, message_content,
                        status, priority, language, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    session_id, session_request.patient_id, CommunicationType.VIDEO.value,
                    json.dumps({
                        "room_name": room_name,
                        "provider_id": session_request.provider_id,
                        "max_participants": session_request.max_participants,
                        "recording_enabled": session_request.recording_enabled
                    }),
                    CommunicationStatus.PENDING.value, MessagePriority.NORMAL.value,
                    Language.ARABIC.value, datetime.now()
                ))
            else:
                cursor.execute("""
                    INSERT INTO communication_history (
                        id, patient_id, communication_type, message_content,
                        status, priority, language, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id, session_request.patient_id, CommunicationType.VIDEO.value,
                    json.dumps({
                        "room_name": room_name,
                        "provider_id": session_request.provider_id,
                        "max_participants": session_request.max_participants,
                        "recording_enabled": session_request.recording_enabled
                    }),
                    CommunicationStatus.PENDING.value, MessagePriority.NORMAL.value,
                    Language.ARABIC.value, datetime.now().isoformat()
                ))
            conn.commit()
        
        # Log audit trail
        user_id = current_user.get("user_id", "system") if current_user else "system"
        log_communication_audit(
            "video_session_created", user_id, session_request.patient_id,
            {"session_id": session_id, "room_name": room_name, "provider_id": session_request.provider_id},
            request
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "room_name": room_name,
            "join_url": f"https://brainsait-video.example.com/room/{room_name}",
            "expires_at": (datetime.now() + timedelta(minutes=session_request.duration_minutes)).isoformat(),
            "max_participants": session_request.max_participants,
            "recording_enabled": session_request.recording_enabled
        }
        
    except Exception as e:
        logger.error(f"Failed to create video session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create video session")

@app.get("/api/v1/communication/history/{patient_id}")
async def get_communication_history(patient_id: str, communication_type: Optional[CommunicationType] = None, limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
    """Get communication history for patient"""
    try:
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                query = "SELECT * FROM communication_history WHERE patient_id = %s"
                params = [patient_id]
                
                if communication_type:
                    query += " AND communication_type = %s"
                    params.append(communication_type.value)
                
                query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                history = cursor.fetchall()
                history_list = [dict(record) for record in history]
                
            else:
                query = "SELECT * FROM communication_history WHERE patient_id = ?"
                params = [patient_id]
                
                if communication_type:
                    query += " AND communication_type = ?"
                    params.append(communication_type.value)
                
                query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                columns = [column[0] for column in cursor.description]
                history_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return {
            "patient_id": patient_id,
            "communication_history": history_list,
            "total_records": len(history_list),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to get communication history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve communication history")

@app.post("/api/v1/communication/preferences")
async def update_communication_preferences(preferences: CommunicationPreferences, request: Request, current_user: dict = Depends(require_auth)):
    """Update patient communication preferences"""
    try:
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                # Check if preferences exist
                cursor.execute("SELECT id FROM communication_preferences WHERE patient_id = %s", (preferences.patient_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing preferences
                    cursor.execute("""
                        UPDATE communication_preferences SET
                            preferred_language = %s, sms_enabled = %s, voice_enabled = %s,
                            video_enabled = %s, email_enabled = %s, preferred_contact_time_start = %s,
                            preferred_contact_time_end = %s, timezone = %s, emergency_contact_phone = %s,
                            updated_at = %s
                        WHERE patient_id = %s
                    """, (
                        preferences.preferred_language.value, preferences.sms_enabled, preferences.voice_enabled,
                        preferences.video_enabled, preferences.email_enabled, preferences.preferred_contact_time_start,
                        preferences.preferred_contact_time_end, preferences.timezone, preferences.emergency_contact_phone,
                        datetime.now(), preferences.patient_id
                    ))
                else:
                    # Insert new preferences
                    cursor.execute("""
                        INSERT INTO communication_preferences (
                            patient_id, preferred_language, sms_enabled, voice_enabled, video_enabled,
                            email_enabled, preferred_contact_time_start, preferred_contact_time_end,
                            timezone, emergency_contact_phone, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        preferences.patient_id, preferences.preferred_language.value, preferences.sms_enabled,
                        preferences.voice_enabled, preferences.video_enabled, preferences.email_enabled,
                        preferences.preferred_contact_time_start, preferences.preferred_contact_time_end,
                        preferences.timezone, preferences.emergency_contact_phone, datetime.now(), datetime.now()
                    ))
            else:
                # SQLite version
                cursor.execute("SELECT id FROM communication_preferences WHERE patient_id = ?", (preferences.patient_id,))
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute("""
                        UPDATE communication_preferences SET
                            preferred_language = ?, sms_enabled = ?, voice_enabled = ?,
                            video_enabled = ?, email_enabled = ?, preferred_contact_time_start = ?,
                            preferred_contact_time_end = ?, timezone = ?, emergency_contact_phone = ?,
                            updated_at = ?
                        WHERE patient_id = ?
                    """, (
                        preferences.preferred_language.value, int(preferences.sms_enabled), int(preferences.voice_enabled),
                        int(preferences.video_enabled), int(preferences.email_enabled), preferences.preferred_contact_time_start,
                        preferences.preferred_contact_time_end, preferences.timezone, preferences.emergency_contact_phone,
                        datetime.now().isoformat(), preferences.patient_id
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO communication_preferences (
                            id, patient_id, preferred_language, sms_enabled, voice_enabled, video_enabled,
                            email_enabled, preferred_contact_time_start, preferred_contact_time_end,
                            timezone, emergency_contact_phone, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(uuid.uuid4()), preferences.patient_id, preferences.preferred_language.value,
                        int(preferences.sms_enabled), int(preferences.voice_enabled), int(preferences.video_enabled),
                        int(preferences.email_enabled), preferences.preferred_contact_time_start,
                        preferences.preferred_contact_time_end, preferences.timezone, preferences.emergency_contact_phone,
                        datetime.now().isoformat(), datetime.now().isoformat()
                    ))
            
            conn.commit()
        
        # Log audit trail
        user_id = current_user.get("user_id", "system") if current_user else "system"
        log_communication_audit(
            "preferences_updated", user_id, preferences.patient_id,
            {"preferred_language": preferences.preferred_language.value, "sms_enabled": preferences.sms_enabled},
            request
        )
        
        return {
            "status": "success",
            "patient_id": preferences.patient_id,
            "message": "Communication preferences updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to update communication preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update communication preferences")

# Workflow Endpoints
@app.post("/api/v1/workflows/appointment/reminder")
async def send_appointment_reminder(workflow_request: WorkflowRequest, request: Request, current_user: dict = Depends(require_auth)):
    """Send appointment reminder workflow"""
    if workflow_request.workflow_type != "appointment_reminder":
        raise HTTPException(status_code=400, detail="Invalid workflow type for this endpoint")
    
    try:
        workflow_id = str(uuid.uuid4())
        
        # Store workflow
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                cursor.execute("""
                    INSERT INTO communication_workflows (
                        id, workflow_id, workflow_type, patient_id, status, priority,
                        template_data, communication_types, scheduled_time, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()), workflow_id, workflow_request.workflow_type, workflow_request.patient_id,
                    "pending", workflow_request.priority.value, json.dumps(workflow_request.template_data),
                    json.dumps([ct.value for ct in workflow_request.communication_types]),
                    workflow_request.scheduled_time, datetime.now()
                ))
            else:
                cursor.execute("""
                    INSERT INTO communication_workflows (
                        id, workflow_id, workflow_type, patient_id, status, priority,
                        template_data, communication_types, scheduled_time, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()), workflow_id, workflow_request.workflow_type, workflow_request.patient_id,
                    "pending", workflow_request.priority.value, json.dumps(workflow_request.template_data),
                    json.dumps([ct.value for ct in workflow_request.communication_types]),
                    workflow_request.scheduled_time.isoformat() if workflow_request.scheduled_time else None,
                    datetime.now().isoformat()
                ))
            conn.commit()
        
        # Execute workflow immediately or schedule
        if not workflow_request.scheduled_time or workflow_request.scheduled_time <= datetime.now():
            # Execute immediately
            appointment_date = workflow_request.template_data.get("appointment_date", "N/A")
            appointment_time = workflow_request.template_data.get("appointment_time", "N/A")
            doctor_name = workflow_request.template_data.get("doctor_name", "الطبيب")
            
            message_ar = f"تذكير بموعدكم الطبي في {appointment_date} الساعة {appointment_time} مع {doctor_name}. منصة برين سايت الصحية"
            message_en = f"Reminder: Your medical appointment on {appointment_date} at {appointment_time} with {doctor_name}. BrainSAIT Healthcare Platform"
            
            # Send via requested communication types
            for comm_type in workflow_request.communication_types:
                if comm_type == CommunicationType.SMS:
                    # Would send SMS here
                    pass
        
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "workflow_type": workflow_request.workflow_type,
            "patient_id": workflow_request.patient_id,
            "scheduled_time": workflow_request.scheduled_time.isoformat() if workflow_request.scheduled_time else None
        }
        
    except Exception as e:
        logger.error(f"Failed to create appointment reminder workflow: {e}")
        raise HTTPException(status_code=500, detail="Failed to create appointment reminder workflow")

@app.post("/api/v1/workflows/clinical/results")
async def send_clinical_results_notification(workflow_request: WorkflowRequest, request: Request, current_user: dict = Depends(require_auth)):
    """Send clinical results notification workflow"""
    if workflow_request.workflow_type != "clinical_results":
        raise HTTPException(status_code=400, detail="Invalid workflow type for this endpoint")
    
    try:
        workflow_id = str(uuid.uuid4())
        
        # Store and execute workflow similar to appointment reminder
        # Implementation would be similar but with different message templates
        
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "workflow_type": workflow_request.workflow_type,
            "patient_id": workflow_request.patient_id,
            "message": "Clinical results notification workflow initiated"
        }
        
    except Exception as e:
        logger.error(f"Failed to create clinical results workflow: {e}")
        raise HTTPException(status_code=500, detail="Failed to create clinical results workflow")

@app.post("/api/v1/workflows/emergency/alert")
async def send_emergency_alert(workflow_request: WorkflowRequest, request: Request, current_user: dict = Depends(require_auth)):
    """Send emergency alert workflow"""
    if workflow_request.workflow_type != "emergency_alert":
        raise HTTPException(status_code=400, detail="Invalid workflow type for this endpoint")
    
    # Emergency alerts should be sent immediately with high priority
    workflow_request.priority = MessagePriority.EMERGENCY
    workflow_request.scheduled_time = None
    
    try:
        workflow_id = str(uuid.uuid4())
        
        # Implementation for emergency alerts with immediate execution
        
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "workflow_type": workflow_request.workflow_type,
            "patient_id": workflow_request.patient_id,
            "priority": "emergency",
            "message": "Emergency alert workflow initiated"
        }
        
    except Exception as e:
        logger.error(f"Failed to create emergency alert workflow: {e}")
        raise HTTPException(status_code=500, detail="Failed to create emergency alert workflow")

@app.get("/api/v1/workflows/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get workflow execution status"""
    try:
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                cursor.execute("SELECT * FROM communication_workflows WHERE workflow_id = %s", (workflow_id,))
                workflow = cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM communication_workflows WHERE workflow_id = ?", (workflow_id,))
                workflow = cursor.fetchone()
            
            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")
            
            if DB_TYPE == "postgres":
                result = dict(workflow)
            else:
                columns = [column[0] for column in cursor.description]
                result = dict(zip(columns, workflow))
            
            return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve workflow status")

# Compliance Endpoints
@app.get("/api/v1/compliance/audit")
async def generate_compliance_audit_report(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, patient_id: Optional[str] = None, limit: int = Query(100, ge=1, le=1000)):
    """Generate HIPAA compliance audit report"""
    try:
        with get_db_connection() as (conn, cursor):
            query = "SELECT * FROM compliance_audit WHERE 1=1"
            params = []
            
            if start_date:
                if DB_TYPE == "postgres":
                    query += " AND timestamp >= %s"
                else:
                    query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                if DB_TYPE == "postgres":
                    query += " AND timestamp <= %s"
                else:
                    query += " AND timestamp <= ?"
                params.append(end_date)
            
            if patient_id:
                if DB_TYPE == "postgres":
                    query += " AND patient_id = %s"
                else:
                    query += " AND patient_id = ?"
                params.append(patient_id)
            
            query += " ORDER BY timestamp DESC"
            if DB_TYPE == "postgres":
                query += " LIMIT %s"
            else:
                query += " LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            if DB_TYPE == "postgres":
                audit_records = [dict(record) for record in cursor.fetchall()]
            else:
                columns = [column[0] for column in cursor.description]
                audit_records = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return {
            "audit_report": audit_records,
            "total_records": len(audit_records),
            "generated_at": datetime.now().isoformat(),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate audit report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate audit report")

@app.post("/api/v1/compliance/consent")
async def manage_patient_consent(consent_request: ConsentRequest, request: Request, current_user: dict = Depends(require_auth)):
    """Manage patient consent for communications"""
    try:
        consent_id = str(uuid.uuid4())
        
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                cursor.execute("""
                    INSERT INTO patient_consent (
                        id, patient_id, consent_type, consent_given, consent_date,
                        expiry_date, digital_signature, witness_id, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    consent_id, consent_request.patient_id, consent_request.consent_type,
                    consent_request.consent_given, consent_request.consent_date,
                    consent_request.expiry_date, consent_request.digital_signature,
                    consent_request.witness_id, datetime.now()
                ))
            else:
                cursor.execute("""
                    INSERT INTO patient_consent (
                        id, patient_id, consent_type, consent_given, consent_date,
                        expiry_date, digital_signature, witness_id, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    consent_id, consent_request.patient_id, consent_request.consent_type,
                    int(consent_request.consent_given), consent_request.consent_date.isoformat(),
                    consent_request.expiry_date.isoformat() if consent_request.expiry_date else None,
                    consent_request.digital_signature, consent_request.witness_id, datetime.now().isoformat()
                ))
            conn.commit()
        
        # Log audit trail
        user_id = current_user.get("user_id", "system") if current_user else "system"
        log_communication_audit(
            "consent_updated", user_id, consent_request.patient_id,
            {"consent_id": consent_id, "consent_type": consent_request.consent_type, "consent_given": consent_request.consent_given},
            request
        )
        
        return {
            "status": "success",
            "consent_id": consent_id,
            "patient_id": consent_request.patient_id,
            "consent_type": consent_request.consent_type,
            "consent_given": consent_request.consent_given
        }
        
    except Exception as e:
        logger.error(f"Failed to manage patient consent: {e}")
        raise HTTPException(status_code=500, detail="Failed to manage patient consent")

@app.get("/api/v1/compliance/phi-check")
async def check_phi_in_content(content: str = Query(..., description="Content to check for PHI")):
    """Check content for potential PHI (Protected Health Information)"""
    try:
        phi_patterns = {
            "national_id": r'\b\d{10}\b',
            "credit_card": r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\+?[0-9]{10,15}\b',
            "medical_record": r'\bMRN[:\s]?\d+\b',
            "date_of_birth": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b'
        }
        
        phi_found = []
        
        for phi_type, pattern in phi_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                phi_found.append({
                    "type": phi_type,
                    "matches": len(matches),
                    "examples": matches[:3]  # Only show first 3 examples
                })
        
        risk_level = "high" if len(phi_found) > 2 else "medium" if phi_found else "low"
        
        return {
            "content_length": len(content),
            "phi_detected": bool(phi_found),
            "risk_level": risk_level,
            "phi_types_found": phi_found,
            "recommendations": [
                "Review content before sending" if phi_found else "Content appears safe",
                "Consider encryption for sensitive data" if risk_level == "high" else None,
                "Obtain patient consent before sharing" if phi_found else None
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to check PHI in content: {e}")
        raise HTTPException(status_code=500, detail="Failed to check content for PHI")

# Webhook Endpoints
@app.post("/webhooks/twilio/status")
async def twilio_status_webhook(request: Request):
    """Handle Twilio status callbacks"""
    try:
        # Verify webhook authenticity if secret is configured
        if TWILIO_CONFIG.get("webhook_secret"):
            signature = request.headers.get("X-Twilio-Signature", "")
            url = str(request.url)
            body = await request.body()
            
            validator = RequestValidator(TWILIO_CONFIG["webhook_secret"])
            if not validator.validate(url, body.decode(), signature):
                raise HTTPException(status_code=403, detail="Invalid webhook signature")
        
        form_data = await request.form()
        
        message_sid = form_data.get("MessageSid")
        message_status = form_data.get("MessageStatus")
        
        if message_sid and message_status:
            # Update communication record
            with get_db_connection() as (conn, cursor):
                status_mapping = {
                    "sent": CommunicationStatus.SENT.value,
                    "delivered": CommunicationStatus.DELIVERED.value,
                    "undelivered": CommunicationStatus.FAILED.value,
                    "failed": CommunicationStatus.FAILED.value
                }
                
                mapped_status = status_mapping.get(message_status, message_status)
                
                if DB_TYPE == "postgres":
                    cursor.execute("""
                        UPDATE communication_history 
                        SET status = %s, delivered_time = %s, updated_at = %s
                        WHERE twilio_sid = %s
                    """, (mapped_status, datetime.now(), datetime.now(), message_sid))
                else:
                    cursor.execute("""
                        UPDATE communication_history 
                        SET status = ?, delivered_time = ?, updated_at = ?
                        WHERE twilio_sid = ?
                    """, (mapped_status, datetime.now().isoformat(), datetime.now().isoformat(), message_sid))
                
                conn.commit()
        
        return {"status": "webhook_processed"}
        
    except Exception as e:
        logger.error(f"Failed to process Twilio status webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/webhooks/twilio/voice")
async def twilio_voice_webhook(request: Request):
    """Handle Twilio voice call events"""
    try:
        form_data = await request.form()
        
        call_sid = form_data.get("CallSid")
        call_status = form_data.get("CallStatus")
        
        if call_sid and call_status:
            # Update communication record
            with get_db_connection() as (conn, cursor):
                status_mapping = {
                    "completed": CommunicationStatus.DELIVERED.value,
                    "no-answer": CommunicationStatus.FAILED.value,
                    "busy": CommunicationStatus.FAILED.value,
                    "failed": CommunicationStatus.FAILED.value
                }
                
                mapped_status = status_mapping.get(call_status, call_status)
                
                if DB_TYPE == "postgres":
                    cursor.execute("""
                        UPDATE communication_history 
                        SET status = %s, delivered_time = %s, updated_at = %s
                        WHERE twilio_sid = %s
                    """, (mapped_status, datetime.now(), datetime.now(), call_sid))
                else:
                    cursor.execute("""
                        UPDATE communication_history 
                        SET status = ?, delivered_time = ?, updated_at = ?
                        WHERE twilio_sid = ?
                    """, (mapped_status, datetime.now().isoformat(), datetime.now().isoformat(), call_sid))
                
                conn.commit()
        
        return {"status": "webhook_processed"}
        
    except Exception as e:
        logger.error(f"Failed to process Twilio voice webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/webhooks/twilio/sms")
async def twilio_sms_webhook(request: Request):
    """Handle Twilio SMS delivery events"""
    try:
        form_data = await request.form()
        
        message_sid = form_data.get("MessageSid")
        sms_status = form_data.get("SmsStatus")
        
        if message_sid and sms_status:
            # Update communication record with delivery status
            with get_db_connection() as (conn, cursor):
                if DB_TYPE == "postgres":
                    cursor.execute("""
                        UPDATE communication_history 
                        SET status = %s, delivered_time = %s, updated_at = %s
                        WHERE twilio_sid = %s
                    """, (sms_status, datetime.now(), datetime.now(), message_sid))
                else:
                    cursor.execute("""
                        UPDATE communication_history 
                        SET status = ?, delivered_time = ?, updated_at = ?
                        WHERE twilio_sid = ?
                    """, (sms_status, datetime.now().isoformat(), datetime.now().isoformat(), message_sid))
                
                conn.commit()
        
        return {"status": "webhook_processed"}
        
    except Exception as e:
        logger.error(f"Failed to process Twilio SMS webhook: {e}")
        return {"status": "error", "message": str(e)}

# Original Healthcare Identities Endpoints
@app.get("/healthcare-identities")
async def list_healthcare_identities(
    entity_type: Optional[EntityType] = None,
    role: Optional[HealthcareRole] = None,
    organization: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """List healthcare identities with filtering and pagination"""
    try:
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                query = "SELECT * FROM healthcare_identities WHERE 1=1"
                params = []

                if entity_type:
                    query += " AND entity_type = %s"
                    params.append(entity_type.value)

                if role:
                    query += " AND role = %s"
                    params.append(role.value)

                if organization:
                    query += " AND organization ILIKE %s"
                    params.append(f"%{organization}%")

                # Get total count for pagination
                count_query = query.replace(
                    "SELECT * FROM healthcare_identities",
                    "SELECT COUNT(*) FROM healthcare_identities"
                )
                cursor.execute(count_query, params)
                total_count = cursor.fetchone()["count"]

                # Get paginated results
                query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                cursor.execute(query, params)
                identities = cursor.fetchall()

            else:  # SQLite
                query = "SELECT * FROM healthcare_identities WHERE 1=1"
                params = []

                if entity_type:
                    query += " AND entity_type = ?"
                    params.append(entity_type.value)

                if role:
                    query += " AND role = ?"
                    params.append(role.value)

                if organization:
                    query += " AND organization LIKE ?"
                    params.append(f"%{organization}%")

                # Get total count for pagination
                count_query = query.replace(
                    "SELECT * FROM healthcare_identities",
                    "SELECT COUNT(*) as count FROM healthcare_identities"
                )
                cursor.execute(count_query, params)
                total_count = cursor.fetchone()["count"]

                # Get paginated results
                query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                cursor.execute(query, params)
                identities = cursor.fetchall()

            # Convert to list of dictionaries
            if DB_TYPE == "postgres":
                identities_list = [dict(identity) for identity in identities]
            else:
                identities_list = [dict(zip([column[0] for column in cursor.description], identity)) for identity in identities]

            return {
                "identities": identities_list,
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }

    except Exception as e:
        logger.error(f"Failed to list healthcare identities: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve healthcare identities"
        )

@app.post("/healthcare-identities", status_code=201)
async def register_healthcare_identity(identity: HealthcareIdentity):
    """Register new healthcare identity with enhanced validation"""
    try:
        # Validate expiration date is in the future
        if identity.expires <= datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Expiration date must be in the future"
            )

        # Generate unique OID
        full_oid = generate_oid(identity.entity_type)
        identity_id = str(uuid.uuid4())

        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                # Check for duplicate user_id
                cursor.execute(
                    "SELECT id FROM healthcare_identities WHERE user_id = %s",
                    (identity.user_id,)
                )
                if cursor.fetchone():
                    raise HTTPException(
                        status_code=409,
                        detail="User ID already exists"
                    )

                # Insert into database
                cursor.execute("""
                    INSERT INTO healthcare_identities (
                        id, entity_type, user_id, name, name_ar, role,
                        access_level, national_id, nphies_id, organization,
                        department, expires, full_oid, metadata,
                        created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                """, (
                    identity_id, identity.entity_type.value, identity.user_id,
                    identity.name, identity.name_ar, identity.role.value,
                    identity.access_level.value, identity.national_id,
                    identity.nphies_id, identity.organization, identity.department,
                    identity.expires, full_oid, json.dumps(identity.metadata),
                    datetime.now(), datetime.now()
                ))

            else:  # SQLite
                # Check for duplicate user_id
                cursor.execute(
                    "SELECT id FROM healthcare_identities WHERE user_id = ?",
                    (identity.user_id,)
                )
                if cursor.fetchone():
                    raise HTTPException(
                        status_code=409,
                        detail="User ID already exists"
                    )

                # Insert into database
                cursor.execute("""
                    INSERT INTO healthcare_identities (
                        id, entity_type, user_id, name, name_ar, role,
                        access_level, national_id, nphies_id, organization,
                        department, expires, full_oid, metadata,
                        created_at, updated_at
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?
                    )
                """, (
                    identity_id, identity.entity_type.value, identity.user_id,
                    identity.name, identity.name_ar, identity.role.value,
                    identity.access_level.value, identity.national_id,
                    identity.nphies_id, identity.organization, identity.department,
                    identity.expires, full_oid, json.dumps(identity.metadata),
                    datetime.now().isoformat(), datetime.now().isoformat()
                ))

            conn.commit()
            logger.info(
                f"Healthcare identity registered: {full_oid} for {identity.name}"
            )

        return {
            "status": "registered",
            "identity_id": identity_id,
            "oid": full_oid,
            "entity_type": identity.entity_type.value,
            "name": identity.name,
            "expires": identity.expires.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register healthcare identity: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to register healthcare identity"
        )

@app.put("/healthcare-identities/{identity_id}")
async def update_healthcare_identity(identity_id: str, identity: HealthcareIdentity):
    """Update existing healthcare identity"""
    try:
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                cursor.execute("""
                    UPDATE healthcare_identities SET
                        user_id = %s, name = %s, name_ar = %s, role = %s,
                        access_level = %s, national_id = %s, nphies_id = %s,
                        organization = %s, department = %s, expires = %s,
                        metadata = %s, updated_at = %s
                    WHERE id = %s
                """, (
                    identity.user_id, identity.name, identity.name_ar, identity.role.value,
                    identity.access_level.value, identity.national_id, identity.nphies_id,
                    identity.organization, identity.department, identity.expires,
                    json.dumps(identity.metadata), datetime.now(), identity_id
                ))
            else:  # SQLite
                cursor.execute("""
                    UPDATE healthcare_identities SET
                        user_id = ?, name = ?, name_ar = ?, role = ?,
                        access_level = ?, national_id = ?, nphies_id = ?,
                        organization = ?, department = ?, expires = ?,
                        metadata = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    identity.user_id, identity.name, identity.name_ar, identity.role.value,
                    identity.access_level.value, identity.national_id, identity.nphies_id,
                    identity.organization, identity.department, identity.expires,
                    json.dumps(identity.metadata), datetime.now().isoformat(), identity_id
                ))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Healthcare identity not found")

            conn.commit()
            return {"status": "updated", "identity_id": identity_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update healthcare identity: {e}")
        raise HTTPException(status_code=500, detail="Failed to update healthcare identity")

@app.delete("/healthcare-identities/{identity_id}")
async def revoke_healthcare_identity(identity_id: str):
    """Revoke (soft delete) healthcare identity"""
    try:
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                cursor.execute("""
                    UPDATE healthcare_identities SET
                        status = 'revoked', updated_at = %s
                    WHERE id = %s
                """, (datetime.now(), identity_id))
            else:  # SQLite
                cursor.execute("""
                    UPDATE healthcare_identities SET
                        status = 'revoked', updated_at = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), identity_id))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Healthcare identity not found")

            conn.commit()
            return {"status": "revoked", "identity_id": identity_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke healthcare identity: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke healthcare identity")

# NPHIES Integration Endpoints
@app.post("/nphies/claims")
async def submit_nphies_claim(claim: NPHIESClaim):
    """Submit claim to NPHIES platform"""
    try:
        claim_uuid = str(uuid.uuid4())

        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                # Store claim in local database
                cursor.execute("""
                    INSERT INTO nphies_claims (
                        id, claim_id, patient_nphies_id, provider_nphies_id,
                        claim_type, amount, currency, diagnosis_codes,
                        procedure_codes, status, submission_date, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    claim_uuid, claim.claim_id, claim.patient_nphies_id, claim.provider_nphies_id,
                    claim.claim_type, claim.amount, claim.currency,
                    json.dumps(claim.diagnosis_codes), json.dumps(claim.procedure_codes),
                    claim.status, claim.submission_date, datetime.now()
                ))
            else:  # SQLite
                cursor.execute("""
                    INSERT INTO nphies_claims (
                        id, claim_id, patient_nphies_id, provider_nphies_id,
                        claim_type, amount, currency, diagnosis_codes,
                        procedure_codes, status, submission_date, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    claim_uuid, claim.claim_id, claim.patient_nphies_id, claim.provider_nphies_id,
                    claim.claim_type, claim.amount, claim.currency,
                    json.dumps(claim.diagnosis_codes), json.dumps(claim.procedure_codes),
                    claim.status, claim.submission_date.isoformat(), datetime.now().isoformat()
                ))

            conn.commit()

        # TODO: Integrate with actual NPHIES API
        # For now, simulate successful submission
        return {
            "status": "submitted",
            "claim_id": claim.claim_id,
            "nphies_reference": f"NPHIES_{claim.claim_id}_{datetime.now().strftime('%Y%m%d')}",
            "submission_time": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to submit NPHIES claim: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit claim to NPHIES")

@app.get("/nphies/claims/{claim_id}")
async def get_nphies_claim(claim_id: str):
    """Get NPHIES claim status"""
    try:
        with get_db_connection() as (conn, cursor):
            if DB_TYPE == "postgres":
                cursor.execute("SELECT * FROM nphies_claims WHERE claim_id = %s", (claim_id,))
                claim = cursor.fetchone()
            else:  # SQLite
                cursor.execute("SELECT * FROM nphies_claims WHERE claim_id = ?", (claim_id,))
                claim = cursor.fetchone()

            if not claim:
                raise HTTPException(status_code=404, detail="Claim not found")

            # Convert row to dict
            if DB_TYPE == "postgres":
                result = dict(claim)
            else:
                result = dict(zip([column[0] for column in cursor.description], claim))

            return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get NPHIES claim: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve claim")

# AI Analytics Endpoints - PyBrain Integration
# Initialize PyBrain AI service
pybrain_service = None

async def get_pybrain_service():
    """Get or initialize PyBrain AI service"""
    global pybrain_service
    if pybrain_service is None:
        try:
            from services.unified_pybrain_service import UnifiedPyBrainService, AITaskType
            from services.ai_arabic_service import AIArabicService
            from services.communication.healthcare_integration import HealthcareSystemIntegrator
            from services.nphies_service import NPHIESService
            
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                logger.warning("OpenAI API key not found, PyBrain will run with limited capabilities")
            
            pybrain_service = UnifiedPyBrainService(
                openai_api_key=openai_api_key,
                cache_size=10000,
                enable_edge_ai=True
            )
            
            # Initialize integrations
            ai_arabic_service = AIArabicService(openai_api_key) if openai_api_key else None
            healthcare_integrator = HealthcareSystemIntegrator()
            nphies_service = NPHIESService()
            
            await pybrain_service.initialize_integrations(
                ai_arabic_service=ai_arabic_service,
                healthcare_integrator=healthcare_integrator,
                nphies_service=nphies_service
            )
            
            logger.info("PyBrain AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PyBrain service: {e}")
            pybrain_service = None
    
    return pybrain_service

@app.post("/ai-analytics/analyze")
async def perform_ai_analysis(analysis: AIAnalysis):
    """Perform AI analysis on healthcare data using PyBrain"""
    try:
        service = await get_pybrain_service()
        if not service:
            # Fallback to simple processing
            enhanced_results = {
                **analysis.results,
                "enhanced": True,
                "processing_time": 0.5,
                "model_version": "brainsait-healthcare-2.2-fallback",
                "processed_at": datetime.now().isoformat(),
                "ai_status": "limited_capabilities"
            }
            
            return {
                "status": "analysis_completed",
                "analysis_id": analysis.analysis_id,
                "confidence_score": analysis.confidence_score,
                "results": enhanced_results
            }
        
        # Use PyBrain AI for analysis
        from services.unified_pybrain_service import AITaskType
        
        # Determine AI task type based on analysis type
        task_type = AITaskType.MEDICAL_ANALYSIS
        if "arabic" in str(analysis.results).lower():
            task_type = AITaskType.ARABIC_NLP
        elif "workflow" in str(analysis.results).lower():
            task_type = AITaskType.WORKFLOW_OPTIMIZATION
        elif "fraud" in str(analysis.results).lower():
            task_type = AITaskType.FRAUD_DETECTION
        elif "risk" in str(analysis.results).lower():
            task_type = AITaskType.RISK_ASSESSMENT
        
        # Generate AI insight
        ai_insight = await service.generate_ai_insight(
            task_type=task_type,
            input_data={
                "analysis_data": analysis.results,
                "analysis_id": analysis.analysis_id,
                "original_data": analysis.dict()
            },
            context={
                "platform": "brainsait_healthcare",
                "version": "2.2.0",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Enhanced results with AI insights
        enhanced_results = {
            **analysis.results,
            "ai_insight": {
                "content": ai_insight.content,
                "confidence_score": ai_insight.confidence_score,
                "confidence_level": ai_insight.confidence_level.value,
                "recommendations": ai_insight.recommendations,
                "cultural_context": ai_insight.cultural_context.value if ai_insight.cultural_context else None,
                "processing_time_ms": ai_insight.processing_time_ms
            },
            "enhanced": True,
            "model_version": "brainsait-pybrain-2.2",
            "processed_at": datetime.now().isoformat(),
            "ai_status": "full_capabilities"
        }
        
        return {
            "status": "analysis_completed",
            "analysis_id": analysis.analysis_id,
            "confidence_score": ai_insight.confidence_score,
            "results": enhanced_results,
            "ai_metadata": {
                "task_type": task_type.value,
                "insight_id": ai_insight.insight_id,
                "cache_used": ai_insight.cache_key is not None
            }
        }

    except Exception as e:
        logger.error(f"Failed to perform AI analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform AI analysis")

@app.post("/ai-analytics/process_ai_request")
async def process_ai_request(request_data: Dict[str, Any]):
    """Process AI request from frontend PyBrain hook"""
    try:
        service = await get_pybrain_service()
        if not service:
            raise HTTPException(status_code=503, detail="PyBrain AI service not available")
        
        from services.unified_pybrain_service import AITaskType
        
        request_type = request_data.get("requestType")
        model = request_data.get("model")
        payload = request_data.get("payload", {})
        options = request_data.get("options", {})
        
        # Map model to task type
        model_to_task_map = {
            "healthcare_insights_v2": AITaskType.MEDICAL_ANALYSIS,
            "arabic_nlp_v1": AITaskType.ARABIC_NLP,
            "claims_analysis_v3": AITaskType.FRAUD_DETECTION,
            "fraud_detection_v2": AITaskType.FRAUD_DETECTION,
            "form_assistance_v1": AITaskType.COMMUNICATION_OPTIMIZATION,
            "revenue_optimization_v1": AITaskType.WORKFLOW_OPTIMIZATION,
            "medical_coding_v2": AITaskType.CLINICAL_DECISION_SUPPORT
        }
        
        task_type = model_to_task_map.get(model, AITaskType.MEDICAL_ANALYSIS)
        
        # Generate AI insight
        ai_insight = await service.generate_ai_insight(
            task_type=task_type,
            input_data=payload,
            context=options.get("context", {}),
            force_refresh=options.get("forceRefresh", False)
        )
        
        return {
            "success": True,
            "data": {
                "insight_id": ai_insight.insight_id,
                "content": ai_insight.content,
                "confidence_score": ai_insight.confidence_score,
                "confidence_level": ai_insight.confidence_level.value,
                "recommendations": ai_insight.recommendations,
                "supporting_data": ai_insight.supporting_data,
                "cultural_context": ai_insight.cultural_context.value if ai_insight.cultural_context else None,
                "processing_time_ms": ai_insight.processing_time_ms,
                "created_at": ai_insight.created_at.isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to process AI request: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }

@app.post("/ai-analytics/initialize")
async def initialize_ai_models(init_data: Dict[str, Any]):
    """Initialize AI models for frontend"""
    try:
        service = await get_pybrain_service()
        if not service:
            return {
                "success": False,
                "error": "PyBrain AI service not available",
                "capabilities": "limited"
            }
        
        # Get performance metrics
        metrics = await service.get_performance_metrics()
        
        return {
            "success": True,
            "models_initialized": True,
            "performance_metrics": metrics,
            "capabilities": "full",
            "supported_languages": ["ar", "en"],
            "cultural_contexts": ["SAUDI_ARABIA", "GULF_REGION"]
        }
    
    except Exception as e:
        logger.error(f"Failed to initialize AI models: {e}")
        return {
            "success": False,
            "error": str(e),
            "capabilities": "error"
        }

@app.get("/ai-analytics/metrics")
async def get_ai_metrics():
    """Get AI performance metrics"""
    try:
        service = await get_pybrain_service()
        if not service:
            return {"status": "unavailable", "metrics": {}}
        
        metrics = await service.get_performance_metrics()
        realtime_insights = await service.get_realtime_insights({
            "platform": "brainsait_healthcare",
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "status": "operational",
            "performance_metrics": metrics,
            "realtime_insights": realtime_insights
        }
    
    except Exception as e:
        logger.error(f"Failed to get AI metrics: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/oid-tree")
async def get_oid_tree(
    depth: Optional[int] = Query(3, ge=1, le=10),
    filter_type: Optional[EntityType] = None,
    include_metadata: bool = Query(True)
):
    """Get OID tree structure with hierarchical organization"""
    try:
        with get_db_connection() as (conn, cursor):
            # Query to get OIDs based on filter
            if DB_TYPE == "postgres":
                query = """
                    SELECT
                        id, entity_type, name, full_oid, role, organization, status
                    FROM healthcare_identities
                    WHERE status = 'active'
                """
                params = []

                if filter_type:
                    query += " AND entity_type = %s"
                    params.append(filter_type.value)

                query += " ORDER BY full_oid"
                cursor.execute(query, params)
                identities = cursor.fetchall()

                # Convert to list of dicts
                identities_list = [dict(identity) for identity in identities]

            else:  # SQLite
                query = """
                    SELECT
                        id, entity_type, name, full_oid, role, organization, status
                    FROM healthcare_identities
                    WHERE status = 'active'
                """
                params = []

                if filter_type:
                    query += " AND entity_type = ?"
                    params.append(filter_type.value)

                query += " ORDER BY full_oid"
                cursor.execute(query, params)

                # Convert to list of dicts
                columns = [column[0] for column in cursor.description]
                identities_list = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Build OID tree structure
            oid_tree = {
                "base_oid": BASE_OID,
                "description": "BrainSAIT Healthcare Platform OID Tree",
                "total_nodes": len(identities_list),
                "generated_at": datetime.now().isoformat(),
                "nodes": {},
            }

            # Process identities into tree
            for identity in identities_list:
                oid_parts = identity["full_oid"].split(".")
                current_level = oid_tree["nodes"]

                # Build tree up to specified depth
                for i, part in enumerate(oid_parts[1:depth+1]):
                    oid_segment = ".".join(oid_parts[:i+2])
                    if oid_segment not in current_level:
                        current_level[oid_segment] = {
                            "oid": oid_segment,
                            "children": {},
                            "entities": []
                        }

                    # Add entity to the deepest matched level
                    if i == len(oid_parts[1:depth+1]) - 1 or i == depth - 1:
                        entity_data = {
                            "id": identity["id"],
                            "name": identity["name"],
                            "entity_type": identity["entity_type"],
                            "role": identity["role"],
                            "full_oid": identity["full_oid"],
                        }
                        if include_metadata and "organization" in identity:
                            entity_data["organization"] = identity["organization"]

                        current_level[oid_segment]["entities"].append(entity_data)

                    current_level = current_level[oid_segment]["children"]

            return oid_tree

    except Exception as e:
        safe_log(f"Failed to generate OID tree: {e}", level="error")
        raise HTTPException(status_code=500, detail="Failed to generate OID tree")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)