"""
Backend Security Utilities for BrainSAIT Healthcare Platform
Provides input validation, sanitization, and security helpers for FastAPI
"""

import re
import html
import logging
import hashlib
import secrets
from typing import Any, Dict, Optional
from datetime import datetime, timezone
from functools import wraps
from fastapi import HTTPException, Request
from pydantic import BaseModel, field_validator

# Configure secure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Security constants
MAX_STRING_LENGTH = 1000
MAX_TEXT_LENGTH = 5000
SENSITIVE_FIELDS = {
    'password', 'token', 'secret', 'key', 'credential', 'auth',
    'ssn', 'social', 'dob', 'date_of_birth', 'medical_record',
    'patient_id', 'national_id', 'passport', 'visa', 'iban'
}

class SecurityError(Exception):
    """Custom security exception"""
    pass

def sanitize_string(input_str: str, max_length: int = MAX_STRING_LENGTH) -> str:
    """
    Sanitize string input to prevent injection attacks

    Args:
        input_str: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        SecurityError: If input is too long or contains dangerous patterns
    """
    if not isinstance(input_str, str):
        input_str = str(input_str)

    # Check length
    if len(input_str) > max_length:
        raise SecurityError(f"Input too long: {len(input_str)} > {max_length}")

    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', input_str)

    # Escape HTML entities
    sanitized = html.escape(sanitized)

    # Remove potential script tags and dangerous patterns
    dangerous_patterns = [
        r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',
        r'javascript:',
        r'on\w+\s*=',
        r'eval\s*\(',
        r'expression\s*\(',
        r'vbscript:',
        r'data:text/html'
    ]

    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

    return sanitized.strip()

def validate_nphies_id(nphies_id: str) -> bool:
    """
    Validate NPHIES ID format

    Args:
        nphies_id: NPHIES ID to validate

    Returns:
        True if valid format
    """
    if not isinstance(nphies_id, str):
        return False

    # NPHIES ID format: NPHIES_ followed by alphanumeric
    pattern = r'^NPHIES_[A-Z0-9_]{1,50}$'
    return bool(re.match(pattern, nphies_id))

def validate_email(email: str) -> bool:
    """
    Validate email address with enhanced security

    Args:
        email: Email to validate

    Returns:
        True if valid
    """
    if not isinstance(email, str) or len(email) > 254:
        return False

    # Enhanced email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_healthcare_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize healthcare data object

    Args:
        data: Dictionary containing healthcare data

    Returns:
        Sanitized data dictionary
    """
    sanitized = {}

    for key, value in data.items():
        if isinstance(value, str):
            if 'id' in key.lower() or 'identifier' in key.lower():
                # Only allow alphanumeric and specific characters for IDs
                sanitized[key] = re.sub(r'[^a-zA-Z0-9\-_.]', '', value)[:100]
            elif 'name' in key.lower() or 'description' in key.lower():
                sanitized[key] = sanitize_string(value, MAX_TEXT_LENGTH)
            else:
                sanitized[key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_healthcare_data(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_healthcare_data(item) if isinstance(item, dict)
                else sanitize_string(str(item)) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized

def redact_sensitive_data(data: Any) -> Any:
    """
    Redact sensitive information from data for logging

    Args:
        data: Data to redact (dict, list, or primitive)

    Returns:
        Data with sensitive fields redacted
    """
    if isinstance(data, dict):
        redacted = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_FIELDS or any(field in key.lower() for field in SENSITIVE_FIELDS):
                redacted[key] = '[REDACTED]'
            else:
                redacted[key] = redact_sensitive_data(value)
        return redacted
    elif isinstance(data, list):
        return [redact_sensitive_data(item) for item in data]
    else:
        return data

def safe_log(message: str, data: Any = None, level: str = 'info') -> None:
    """
    Safely log message with data redaction

    Args:
        message: Log message
        data: Additional data to log (will be redacted)
        level: Log level (debug, info, warning, error)
    """
    # Sanitize message
    safe_message = sanitize_string(message, 500)

    # Redact sensitive data
    safe_data = redact_sensitive_data(data) if data else None

    # Create timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    # Format log entry
    if safe_data:
        log_entry = f"[{timestamp}] {safe_message} | Data: {safe_data}"
    else:
        log_entry = f"[{timestamp}] {safe_message}"

    # Log with appropriate level
    getattr(logger, level.lower(), logger.info)(log_entry)

def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure token

    Args:
        length: Token length in bytes

    Returns:
        Hex-encoded secure token
    """
    return secrets.token_hex(length)

def hash_sensitive_data(data: str, salt: Optional[str] = None) -> str:
    """
    Hash sensitive data with salt

    Args:
        data: Data to hash
        salt: Optional salt (will generate if not provided)

    Returns:
        Hashed data
    """
    if salt is None:
        salt = secrets.token_hex(16)

    # Use SHA-256 with salt
    hasher = hashlib.sha256()
    hasher.update(salt.encode('utf-8'))
    hasher.update(data.encode('utf-8'))

    return f"{salt}:{hasher.hexdigest()}"

def verify_hashed_data(data: str, hashed: str) -> bool:
    """
    Verify data against hash

    Args:
        data: Original data
        hashed: Hashed data with salt

    Returns:
        True if data matches hash
    """
    try:
        salt, hash_value = hashed.split(':', 1)
        return hash_sensitive_data(data, salt) == hashed
    except (ValueError, AttributeError):
        return False

class SecurityMiddleware:
    """Security middleware for FastAPI"""

    def __init__(self, max_requests_per_minute: int = 100):
        self.max_requests_per_minute = max_requests_per_minute
        self.request_counts = {}

    async def __call__(self, request: Request, call_next):
        # Rate limiting
        client_ip = request.client.host
        current_minute = datetime.now().minute

        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {}

        if current_minute not in self.request_counts[client_ip]:
            self.request_counts[client_ip] = {current_minute: 0}

        self.request_counts[client_ip][current_minute] += 1

        if self.request_counts[client_ip][current_minute] > self.max_requests_per_minute:
            safe_log(f"Rate limit exceeded for IP: {client_ip}", level='warning')
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Security headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response

def require_auth(func):
    """
    Decorator to require authentication for endpoints

    Args:
        func: Function to wrap

    Returns:
        Wrapped function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # This is a placeholder for actual auth implementation
        # In production, validate JWT token, check permissions, etc.
        return await func(*args, **kwargs)

    return wrapper

def audit_log(action: str, user_id: str, resource_type: str,
              resource_id: Optional[str] = None, metadata: Optional[Dict] = None) -> None:
    """
    Log audit event for healthcare compliance

    Args:
        action: Action performed
        user_id: User performing action
        resource_type: Type of resource accessed
        resource_id: ID of resource (will be redacted in logs)
        metadata: Additional metadata
    """
    audit_data = {
        'action': sanitize_string(action),
        'user_id': sanitize_string(user_id),
        'resource_type': sanitize_string(resource_type),
        'resource_id': '[REDACTED]' if resource_id else None,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'metadata': redact_sensitive_data(metadata) if metadata else None
    }

    safe_log(f"AUDIT: {action} on {resource_type} by user {user_id}", audit_data, 'info')

class SecureHealthcareModel(BaseModel):
    """Base model with built-in security validations"""

    model_config = {
        # Validate assignment to prevent injection
        'validate_assignment': True,
        # Use enum values
        'use_enum_values': True,
        # Allow population by field name (Pydantic V2)
        'populate_by_name': True
    }

    @field_validator('*', mode='before')
    @classmethod
    def sanitize_strings(cls, v):
        """Sanitize all string fields"""
        if isinstance(v, str):
            return sanitize_string(v)
        return v

# Input validation schemas
class NphiesIdModel(BaseModel):
    nphies_id: str

    @field_validator('nphies_id')
    @classmethod
    def validate_nphies_id(cls, v):
        if not validate_nphies_id(v):
            raise ValueError('Invalid NPHIES ID format')
        return v

class EmailModel(BaseModel):
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not validate_email(v):
            raise ValueError('Invalid email format')
        return v

# Export security utilities
__all__ = [
    'sanitize_string',
    'validate_nphies_id',
    'validate_email',
    'sanitize_healthcare_data',
    'redact_sensitive_data',
    'safe_log',
    'generate_secure_token',
    'hash_sensitive_data',
    'verify_hashed_data',
    'SecurityMiddleware',
    'require_auth',
    'audit_log',
    'SecureHealthcareModel',
    'NphiesIdModel',
    'EmailModel',
    'SecurityError'
]
