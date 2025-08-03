"""
PyTest Configuration for HIPAA-Compliant Twilio Integration Tests
================================================================

Global test configuration, fixtures, and utilities for the BrainSAIT
HIPAA-compliant communication testing framework.
"""

import pytest
import asyncio
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List, Optional
import json
import uuid

# Test configuration
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config():
    """Global test configuration"""
    return {
        "testing_environment": "unit_test",
        "mock_external_services": True,
        "arabic_testing_enabled": True,
        "hipaa_compliance_testing": True,
        "performance_testing_enabled": True,
        "security_testing_enabled": True,
        "test_data_encryption": True,
        "audit_testing": True,
        "twilio_mock_mode": True,
        "database_isolation": True
    }


@pytest.fixture(scope="session")
def temp_test_directory():
    """Create temporary directory for test files"""
    temp_dir = tempfile.mkdtemp(prefix="brainsait_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_twilio_credentials():
    """Mock Twilio credentials for testing"""
    return {
        "account_sid": "test_account_sid_12345",
        "auth_token": "test_auth_token_67890",
        "signing_key_sid": "test_signing_key_abcde",
        "private_key": "test_private_key_fghij",
        "webhook_url": "https://test.brainsait.com/webhooks/twilio",
        "hipaa_enabled": True,
        "region": "riyadh",
        "edge": "sydney"
    }


@pytest.fixture
def mock_encryption_keys():
    """Mock encryption keys for testing"""
    return {
        "primary_key": "test_encryption_key_32_chars_long",
        "key_id": "test_key_123",
        "algorithm": "AES-256-GCM",
        "key_derivation": "PBKDF2-SHA256",
        "rotation_schedule": "quarterly",
        "backup_keys": ["backup_key_1", "backup_key_2"]
    }


@pytest.fixture
def sample_patients():
    """Sample patient data for testing"""
    return [
        {
            "id": "patient_arabic_123",
            "name_en": "Ahmed Mohammed Al-Rashid",
            "name_ar": "أحمد محمد الراشد",
            "phone": "+966501234567",
            "email": "ahmed.mohammed@email.com",
            "language_preference": "ar",
            "communication_preferences": {
                "sms": True,
                "voice": True,
                "email": False,
                "preferred_time": "morning"
            },
            "emergency_contact": "+966507654321",
            "national_id": "1234567890",
            "consent_status": "active",
            "hipaa_consent_date": "2024-01-15T10:30:00Z"
        },
        {
            "id": "patient_english_456",
            "name_en": "Sarah Johnson",
            "name_ar": "سارة جونسون",
            "phone": "+966503456789",
            "email": "sarah.johnson@email.com",
            "language_preference": "en",
            "communication_preferences": {
                "sms": True,
                "voice": False,
                "email": True,
                "preferred_time": "afternoon"
            },
            "emergency_contact": "+966509876543",
            "national_id": "9876543210",
            "consent_status": "active",
            "hipaa_consent_date": "2024-02-20T14:15:00Z"
        },
        {
            "id": "patient_minor_789",
            "name_en": "Omar Abdullah",
            "name_ar": "عمر عبدالله",
            "phone": "+966505555555",
            "email": "omar.guardian@email.com",
            "language_preference": "ar",
            "age": 16,
            "guardian_id": "guardian_123",
            "guardian_consent": True,
            "communication_preferences": {
                "sms": False,
                "voice": True,
                "email": False,
                "guardian_notification": True
            },
            "emergency_contact": "+966506666666",
            "national_id": "5555444433",
            "consent_status": "guardian_consent",
            "hipaa_consent_date": "2024-03-10T09:45:00Z"
        }
    ]


@pytest.fixture
def sample_providers():
    """Sample healthcare provider data for testing"""
    return [
        {
            "id": "provider_doctor_123",
            "name_en": "Dr. Fatima Al-Zahra",
            "name_ar": "د. فاطمة الزهراء",
            "specialty": "cardiology",
            "department": "cardiac_care",
            "phone": "+966511111111",
            "email": "fatima.alzahra@brainsait.com",
            "license_number": "DOC123456",
            "communication_capabilities": [
                "patient_communications",
                "emergency_alerts",
                "care_coordination"
            ],
            "on_call_status": True,
            "hipaa_training_completed": True,
            "last_training_date": "2024-01-30T08:00:00Z"
        },
        {
            "id": "provider_nurse_456", 
            "name_en": "Nurse Khalid Al-Mansouri",
            "name_ar": "الممرض خالد المنصوري",
            "specialty": "emergency_care",
            "department": "emergency_department",
            "phone": "+966522222222",
            "email": "khalid.mansouri@brainsait.com",
            "license_number": "NUR789012",
            "communication_capabilities": [
                "patient_communications",
                "emergency_alerts"
            ],
            "on_call_status": False,
            "hipaa_training_completed": True,
            "last_training_date": "2024-02-15T10:30:00Z"
        }
    ]


@pytest.fixture
def sample_workflows():
    """Sample workflow configurations for testing"""
    return {
        "pre_visit": {
            "workflow_id": "pre_visit_std",
            "name": "Standard Pre-Visit Workflow",
            "steps": [
                {
                    "step_id": "appointment_confirmation",
                    "type": "sms",
                    "timing": "24_hours_before",
                    "template": "appointment_confirmation_template",
                    "language_specific": True
                },
                {
                    "step_id": "preparation_instructions",
                    "type": "sms",
                    "timing": "12_hours_before",
                    "template": "preparation_instructions_template",
                    "language_specific": True
                },
                {
                    "step_id": "insurance_verification",
                    "type": "sms",
                    "timing": "6_hours_before",
                    "template": "insurance_verification_template",
                    "language_specific": True
                }
            ],
            "triggers": ["appointment_scheduled"],
            "conditions": {
                "patient_consent_required": True,
                "appointment_type": ["consultation", "procedure"],
                "minimum_advance_notice": "24_hours"
            }
        },
        "emergency": {
            "workflow_id": "emergency_alert",
            "name": "Emergency Alert Workflow",
            "steps": [
                {
                    "step_id": "immediate_alert",
                    "type": "voice",
                    "timing": "immediate",
                    "template": "emergency_alert_template",
                    "broadcast": True
                },
                {
                    "step_id": "response_confirmation",
                    "type": "sms",
                    "timing": "2_minutes_after",
                    "template": "response_confirmation_template",
                    "response_required": True
                }
            ],
            "triggers": ["code_blue", "fire_alarm", "security_alert"],
            "conditions": {
                "severity_level": ["critical", "urgent"],
                "location_specific": True,
                "response_team_required": True
            }
        }
    }


@pytest.fixture
def sample_templates():
    """Sample message templates for testing"""
    return {
        "appointment_confirmation": {
            "en": {
                "sms": "Hi {patient_name}, your appointment with {provider_name} is confirmed for {appointment_date} at {appointment_time}. Location: {location}. Reply CONFIRM or call {phone}.",
                "voice": "Hello {patient_name}. This is BrainSAIT Healthcare confirming your appointment with {provider_name} scheduled for {appointment_date} at {appointment_time}."
            },
            "ar": {
                "sms": "مرحباً {patient_name}، موعدك مع {provider_name} مؤكد في {appointment_date} الساعة {appointment_time}. الموقع: {location}. رد بـ تأكيد أو اتصل {phone}.",
                "voice": "مرحباً {patient_name}. هذه مستشفى برين سايت تؤكد موعدك مع {provider_name} المحدد في {appointment_date} الساعة {appointment_time}."
            }
        },
        "emergency_alert": {
            "en": {
                "voice": "Emergency alert: {alert_type} in {location}. Response team {response_team} report immediately. This is not a drill.",
                "sms": "EMERGENCY: {alert_type} - {location}. Report immediately if you are {response_team}. Confirm receipt."
            },
            "ar": {
                "voice": "تنبيه طارئ: {alert_type} في {location}. على فريق الاستجابة {response_team} التوجه فوراً. هذا ليس تدريباً.",
                "sms": "طارئ: {alert_type} - {location}. توجه فوراً إذا كنت من {response_team}. أكد الاستلام."
            }
        }
    }


@pytest.fixture
def mock_audit_events():
    """Sample audit events for testing"""
    return [
        {
            "audit_id": f"audit_{uuid.uuid4()}",
            "timestamp": datetime.now() - timedelta(minutes=30),
            "event_type": "communication_sent",
            "user_id": "doctor_123",
            "patient_id": "patient_456",
            "action": "sms_sent",
            "resource": "patient_communication",
            "phi_accessed": False,
            "hipaa_compliant": True,
            "ip_address": "192.168.1.100",
            "user_agent": "BrainSAIT/1.0",
            "session_id": "session_123"
        },
        {
            "audit_id": f"audit_{uuid.uuid4()}",
            "timestamp": datetime.now() - timedelta(minutes=15),
            "event_type": "phi_access",
            "user_id": "nurse_456",
            "patient_id": "patient_789",
            "action": "communication_history_viewed",
            "resource": "patient_communication_logs",
            "phi_accessed": True,
            "hipaa_compliant": True,
            "access_reason": "patient_care",
            "ip_address": "192.168.1.101",
            "user_agent": "BrainSAIT/1.0",
            "session_id": "session_456"
        }
    ]


@pytest.fixture
def mock_compliance_metrics():
    """Mock compliance metrics for testing"""
    return {
        "overall_compliance_score": 98.5,
        "audit_trail_integrity": 100.0,
        "phi_detection_accuracy": 97.8,
        "encryption_coverage": 100.0,
        "consent_compliance": 99.2,
        "access_control_effectiveness": 98.1,
        "breach_detection_time_avg": 2.5,  # minutes
        "notification_compliance": 100.0,
        "staff_training_completion": 96.0,
        "vulnerability_remediation": 99.0,
        "policy_adherence": 97.5,
        "last_assessment": datetime.now() - timedelta(hours=1),
        "next_assessment": datetime.now() + timedelta(hours=23)
    }


@pytest.fixture
async def mock_twilio_client():
    """Mock Twilio client for testing"""
    client = Mock()
    
    # Mock SMS methods
    client.messages = Mock()
    client.messages.create = AsyncMock(return_value=Mock(
        sid="SM1234567890abcdef",
        status="sent",
        to="+966501234567",
        from_="+966507654321",
        body="Test message",
        date_created=datetime.now(),
        price="0.05",
        price_unit="USD"
    ))
    
    # Mock Voice methods
    client.calls = Mock()
    client.calls.create = AsyncMock(return_value=Mock(
        sid="CA1234567890abcdef",
        status="initiated",
        to="+966501234567",
        from_="+966507654321",
        duration=None,
        start_time=datetime.now()
    ))
    
    # Mock Recordings
    client.recordings = Mock()
    client.recordings.list = AsyncMock(return_value=[
        Mock(
            sid="RE1234567890abcdef",
            account_sid="AC1234567890abcdef",
            call_sid="CA1234567890abcdef",
            status="completed",
            duration="125",
            date_created=datetime.now()
        )
    ])
    
    return client


@pytest.fixture
def mock_database_session():
    """Mock database session for testing"""
    session = Mock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def arabic_test_data():
    """Arabic text samples for testing"""
    return {
        "medical_terms": [
            "داء السكري",  # diabetes
            "ارتفاع ضغط الدم",  # hypertension
            "فحص الدم",  # blood test
            "أشعة سينية",  # x-ray
            "تخطيط القلب",  # ECG
            "العلاج الطبيعي",  # physical therapy
            "الطب النفسي",  # psychiatry
            "جراحة القلب"  # cardiac surgery
        ],
        "patient_names": [
            "أحمد محمد الراشد",
            "فاطمة علي النجار",
            "خالد عبدالله السعيد",
            "نورا إبراهيم الغامدي",
            "عبدالرحمن صالح القحطاني"
        ],
        "appointment_messages": [
            "موعدك مؤكد غداً الساعة الثانية ظهراً",
            "يرجى الحضور قبل الموعد بنصف ساعة",
            "لا تنس إحضار بطاقة التأمين الطبي",
            "في حالة عدم القدرة على الحضور، يرجى الاتصال",
            "نتائج الفحوصات جاهزة للمراجعة"
        ],
        "phi_samples": [
            "رقم الهوية: 1234567890",
            "رقم الهاتف: 0501234567",
            "البريد الإلكتروني: patient@email.com",
            "رقم السجل الطبي: MRN123456",
            "تاريخ الميلاد: 15/03/1985"
        ]
    }


# Test utilities
class TestUtilities:
    """Utility functions for testing"""
    
    @staticmethod
    def generate_test_message_id():
        """Generate test message ID"""
        return f"test_msg_{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def generate_test_patient_id():
        """Generate test patient ID"""
        return f"test_patient_{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def create_mock_webhook_signature(payload: str, auth_token: str) -> str:
        """Create mock webhook signature"""
        import hmac
        import hashlib
        import base64
        
        signature = hmac.new(
            auth_token.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def validate_arabic_text(text: str) -> bool:
        """Validate Arabic text contains Arabic characters"""
        arabic_range = range(0x0600, 0x06FF + 1)
        return any(ord(char) in arabic_range for char in text)
    
    @staticmethod
    def simulate_network_delay(delay_seconds: float = 0.1):
        """Simulate network delay for testing"""
        import time
        time.sleep(delay_seconds)


@pytest.fixture
def test_utilities():
    """Test utilities fixture"""
    return TestUtilities


# Performance testing utilities
@pytest.fixture
def performance_monitor():
    """Performance monitoring utilities"""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            
        def start(self):
            import time
            self.start_time = time.time()
            
        def stop(self):
            import time
            self.end_time = time.time()
            
        def elapsed_time(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
            
        def assert_performance(self, max_time_seconds: float):
            elapsed = self.elapsed_time()
            assert elapsed is not None, "Performance monitoring not started/stopped"
            assert elapsed <= max_time_seconds, f"Performance exceeded limit: {elapsed}s > {max_time_seconds}s"
    
    return PerformanceMonitor()


# Security testing utilities
@pytest.fixture
def security_scanner():
    """Security testing utilities"""
    class SecurityScanner:
        @staticmethod
        def check_for_sql_injection(input_string: str) -> bool:
            """Check for SQL injection patterns"""
            sql_injection_patterns = [
                "' OR '1'='1",
                "'; DROP TABLE",
                "' UNION SELECT",
                "' OR 1=1",
                "--",
                "/*",
                "*/"
            ]
            return any(pattern in input_string.upper() for pattern in sql_injection_patterns)
        
        @staticmethod
        def check_for_xss(input_string: str) -> bool:
            """Check for XSS patterns"""
            xss_patterns = [
                "<script>",
                "javascript:",
                "onload=",
                "onerror=",
                "<%",
                "%>",
                "${",
                "}"
            ]
            return any(pattern in input_string.lower() for pattern in xss_patterns)
        
        @staticmethod
        def validate_encryption_strength(algorithm: str, key_size: int) -> bool:
            """Validate encryption meets security standards"""
            secure_algorithms = ["AES-256-GCM", "AES-256-CBC", "ChaCha20-Poly1305"]
            minimum_key_sizes = {"AES": 256, "ChaCha20": 256}
            
            if algorithm not in secure_algorithms:
                return False
                
            algo_type = algorithm.split("-")[0]
            if algo_type in minimum_key_sizes:
                return key_size >= minimum_key_sizes[algo_type]
                
            return True
    
    return SecurityScanner()


# Pytest hooks for custom behavior
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "hipaa: mark test as HIPAA compliance test"
    )
    config.addinivalue_line(
        "markers", "arabic: mark test as Arabic language test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add custom markers"""
    for item in items:
        # Add markers based on test file names
        if "hipaa" in item.nodeid.lower():
            item.add_marker(pytest.mark.hipaa)
        if "arabic" in item.nodeid.lower():
            item.add_marker(pytest.mark.arabic)
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        if "performance" in item.nodeid.lower():
            item.add_marker(pytest.mark.performance)
        if "security" in item.nodeid.lower():
            item.add_marker(pytest.mark.security)


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test"""
    yield
    # Cleanup code here (clear mocks, reset state, etc.)
    pass


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before all tests"""
    # Set environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["TWILIO_MOCK_MODE"] = "true"
    os.environ["HIPAA_COMPLIANCE_TESTING"] = "true"
    
    yield
    
    # Cleanup environment after tests
    os.environ.pop("TESTING", None)
    os.environ.pop("TWILIO_MOCK_MODE", None)
    os.environ.pop("HIPAA_COMPLIANCE_TESTING", None)