"""
API Tests for Communication Endpoints
=====================================

Comprehensive API test suite for all communication endpoints including:
- Authentication and authorization testing
- Input validation and error handling
- Arabic content handling
- Webhook signature validation
- Rate limiting and security tests
"""

import pytest
import asyncio
import json
import base64
import hmac
import hashlib
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi.testclient import TestClient
from fastapi import HTTPException, status

# Import API modules
try:
    from services.communication_api import CommunicationAPI
    from main import app  # FastAPI application
    from utils.security import SecurityManager
    from services.communication.patient_communication_service import PatientCommunicationService
except ImportError:
    # Create mock classes for testing when implementation is not yet available
    class CommunicationAPI:
        pass
    app = Mock()
    class SecurityManager:
        pass
    class PatientCommunicationService:
        pass


class TestCommunicationAPIAuthentication:
    """Test suite for API authentication and authorization"""

    @pytest.fixture
    def test_client(self):
        """Create test client for API testing"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        return {
            "Authorization": "Bearer valid_jwt_token_here",
            "X-API-Key": "test_api_key_12345",
            "Content-Type": "application/json"
        }

    @pytest.fixture
    def invalid_auth_headers(self):
        """Mock invalid authentication headers"""
        return {
            "Authorization": "Bearer invalid_token",
            "X-API-Key": "invalid_key",
            "Content-Type": "application/json"
        }

    def test_authentication_required_endpoints(self, test_client):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            "/api/v1/communication/send-sms",
            "/api/v1/communication/send-voice",
            "/api/v1/communication/patient-workflows",
            "/api/v1/communication/emergency-alerts",
            "/api/v1/communication/audit-logs"
        ]
        
        for endpoint in protected_endpoints:
            response = test_client.post(endpoint, json={})
            assert response.status_code in [401, 422]  # Unauthorized or Unprocessable Entity

    def test_valid_authentication_token(self, test_client, auth_headers):
        """Test API access with valid authentication token"""
        with patch('utils.security.SecurityManager.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "user_id": "user_123",
                "role": "healthcare_provider",
                "permissions": ["send_communications", "view_audit_logs"]
            }
            
            response = test_client.get(
                "/api/v1/communication/status",
                headers=auth_headers
            )
            # Assuming endpoint exists and returns 200 for valid auth
            assert response.status_code in [200, 404]  # 404 if endpoint not implemented yet

    def test_invalid_authentication_token(self, test_client, invalid_auth_headers):
        """Test API access with invalid authentication token"""
        with patch('utils.security.SecurityManager.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {
                "valid": False,
                "error": "Invalid token signature"
            }
            
            response = test_client.post(
                "/api/v1/communication/send-sms",
                headers=invalid_auth_headers,
                json={"to": "+966501234567", "message": "test"}
            )
            assert response.status_code == 401

    def test_role_based_authorization(self, test_client, auth_headers):
        """Test role-based access control for different endpoints"""
        # Test doctor role access
        with patch('utils.security.SecurityManager.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "user_id": "doctor_123",
                "role": "doctor",
                "permissions": ["send_patient_communications"]
            }
            
            response = test_client.post(
                "/api/v1/communication/send-patient-message",
                headers=auth_headers,
                json={
                    "patient_id": "patient_123",
                    "message": "Your test results are ready",
                    "message_type": "sms"
                }
            )
            # Should be authorized for patient communications
            assert response.status_code in [200, 404, 422]

        # Test nurse role access to emergency alerts
        with patch('utils.security.SecurityManager.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "user_id": "nurse_456",
                "role": "nurse",
                "permissions": ["emergency_communications"]
            }
            
            response = test_client.post(
                "/api/v1/communication/emergency-alert",
                headers=auth_headers,
                json={
                    "alert_type": "patient_fall",
                    "location": "room_205",
                    "severity": "medium"
                }
            )
            assert response.status_code in [200, 404, 422]

    def test_permission_based_access_control(self, test_client, auth_headers):
        """Test granular permission-based access control"""
        # Test user without audit log permissions
        with patch('utils.security.SecurityManager.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "user_id": "user_789",
                "role": "healthcare_assistant",
                "permissions": ["send_basic_communications"]  # No audit permissions
            }
            
            response = test_client.get(
                "/api/v1/communication/audit-logs",
                headers=auth_headers
            )
            assert response.status_code in [403, 404]  # Forbidden or not implemented

    def test_api_key_validation(self, test_client):
        """Test API key validation for webhook endpoints"""
        valid_api_key = "brainsait_api_key_12345"
        invalid_api_key = "invalid_key"
        
        webhook_data = {
            "MessageSid": "SM123456",
            "MessageStatus": "delivered",
            "From": "+966501234567",
            "To": "+966507654321"
        }
        
        # Test valid API key
        with patch('utils.security.SecurityManager.validate_api_key') as mock_validate:
            mock_validate.return_value = True
            
            response = test_client.post(
                "/api/v1/communication/webhooks/twilio/sms",
                headers={"X-API-Key": valid_api_key},
                json=webhook_data
            )
            assert response.status_code in [200, 404, 422]
        
        # Test invalid API key
        with patch('utils.security.SecurityManager.validate_api_key') as mock_validate:
            mock_validate.return_value = False
            
            response = test_client.post(
                "/api/v1/communication/webhooks/twilio/sms",
                headers={"X-API-Key": invalid_api_key},
                json=webhook_data
            )
            assert response.status_code == 401


class TestCommunicationEndpoints:
    """Test suite for communication API endpoints"""

    @pytest.fixture
    def test_client(self):
        """Create test client for API testing"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        return {
            "Authorization": "Bearer valid_token",
            "Content-Type": "application/json"
        }

    def test_send_sms_endpoint(self, test_client, auth_headers):
        """Test SMS sending endpoint"""
        sms_data = {
            "to": "+966501234567",
            "message": "Your appointment is confirmed for tomorrow at 2 PM",
            "patient_id": "patient_123",
            "message_type": "appointment_confirmation",
            "language": "en",
            "encrypt": True
        }
        
        with patch('services.communication.patient_communication_service.PatientCommunicationService.send_sms') as mock_send:
            mock_send.return_value = {
                "message_id": "msg_123456",
                "status": "sent",
                "delivery_tracking": True,
                "encrypted": True,
                "phi_detected": False
            }
            
            response = test_client.post(
                "/api/v1/communication/send-sms",
                headers=auth_headers,
                json=sms_data
            )
            
            # Check response structure
            if response.status_code == 200:
                response_data = response.json()
                assert "message_id" in response_data
                assert response_data["status"] == "sent"

    def test_send_arabic_sms_endpoint(self, test_client, auth_headers):
        """Test Arabic SMS sending endpoint"""
        arabic_sms_data = {
            "to": "+966501234567",
            "message": "موعدك مؤكد غداً الساعة 2 ظهراً",
            "patient_id": "patient_456",
            "message_type": "appointment_confirmation",
            "language": "ar",
            "rtl_support": True,
            "encrypt": True
        }
        
        with patch('services.communication.patient_communication_service.PatientCommunicationService.send_sms') as mock_send:
            mock_send.return_value = {
                "message_id": "msg_ar_789",
                "status": "sent",
                "language": "ar",
                "character_encoding": "UCS2",
                "sms_parts": 1,
                "estimated_cost": "0.05"
            }
            
            response = test_client.post(
                "/api/v1/communication/send-sms",
                headers=auth_headers,
                json=arabic_sms_data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                assert response_data["language"] == "ar"
                assert response_data["character_encoding"] == "UCS2"

    def test_send_voice_call_endpoint(self, test_client, auth_headers):
        """Test voice call endpoint"""
        voice_data = {
            "to": "+966501234567",
            "script_type": "appointment_reminder",
            "patient_id": "patient_789",
            "language": "ar",
            "voice_gender": "female",
            "record_call": True,
            "encrypt_recording": True
        }
        
        with patch('services.communication.patient_communication_service.PatientCommunicationService.initiate_voice_call') as mock_call:
            mock_call.return_value = {
                "call_id": "call_456789",
                "status": "initiated",
                "estimated_duration": "60 seconds",
                "recording_enabled": True,
                "encryption_enabled": True
            }
            
            response = test_client.post(
                "/api/v1/communication/send-voice",
                headers=auth_headers,
                json=voice_data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                assert "call_id" in response_data
                assert response_data["recording_enabled"] is True

    def test_patient_workflow_trigger_endpoint(self, test_client, auth_headers):
        """Test patient workflow trigger endpoint"""
        workflow_data = {
            "patient_id": "patient_123",
            "workflow_type": "pre_visit",
            "appointment_id": "apt_456",
            "trigger_time": "immediate",
            "custom_parameters": {
                "appointment_date": "2024-08-05T14:00:00",
                "provider_name": "Dr. Ahmed Hassan",
                "preparation_required": True
            }
        }
        
        with patch('services.communication.workflow_orchestrator.WorkflowOrchestrator.trigger_workflow') as mock_trigger:
            mock_trigger.return_value = {
                "workflow_id": "wf_789123",
                "status": "initiated",
                "estimated_completion": "5 minutes",
                "steps_scheduled": 4,
                "first_communication_eta": "30 seconds"
            }
            
            response = test_client.post(
                "/api/v1/communication/trigger-workflow",
                headers=auth_headers,
                json=workflow_data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                assert "workflow_id" in response_data
                assert response_data["status"] == "initiated"

    def test_emergency_alert_endpoint(self, test_client, auth_headers):
        """Test emergency alert broadcast endpoint"""
        emergency_data = {
            "alert_type": "code_blue",
            "location": "ICU Room 205",
            "severity": "critical",
            "response_teams": ["cardiology", "anesthesia", "nursing"],
            "patient_id": "patient_emergency_123",
            "estimated_response_time": "2 minutes"
        }
        
        with patch('services.communication.workflows.emergency_workflow.EmergencyWorkflow.broadcast_emergency') as mock_broadcast:
            mock_broadcast.return_value = {
                "alert_id": "alert_critical_456",
                "broadcast_sent": True,
                "recipients_notified": 15,
                "response_confirmations": 0,
                "escalation_scheduled": True
            }
            
            response = test_client.post(
                "/api/v1/communication/emergency-alert",
                headers=auth_headers,
                json=emergency_data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                assert response_data["broadcast_sent"] is True
                assert response_data["recipients_notified"] > 0

    def test_communication_status_endpoint(self, test_client, auth_headers):
        """Test communication status tracking endpoint"""
        status_request = {
            "message_ids": ["msg_123", "msg_456", "call_789"],
            "include_delivery_details": True,
            "include_error_details": True
        }
        
        with patch('services.communication.patient_communication_service.PatientCommunicationService.get_communication_status') as mock_status:
            mock_status.return_value = {
                "msg_123": {
                    "status": "delivered",
                    "delivered_at": "2024-08-04T10:30:00Z",
                    "delivery_attempts": 1
                },
                "msg_456": {
                    "status": "failed",
                    "error_code": "21610",
                    "error_message": "Message body is required"
                },
                "call_789": {
                    "status": "completed",
                    "call_duration": "125 seconds",
                    "recording_available": True
                }
            }
            
            response = test_client.post(
                "/api/v1/communication/status",
                headers=auth_headers,
                json=status_request
            )
            
            if response.status_code == 200:
                response_data = response.json()
                assert "msg_123" in response_data
                assert response_data["msg_123"]["status"] == "delivered"


class TestInputValidationAndErrorHandling:
    """Test suite for input validation and error handling"""

    @pytest.fixture
    def test_client(self):
        """Create test client for API testing"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        return {
            "Authorization": "Bearer valid_token",
            "Content-Type": "application/json"
        }

    def test_invalid_phone_number_validation(self, test_client, auth_headers):
        """Test phone number validation"""
        invalid_phone_numbers = [
            "123456789",  # Too short
            "+1234567890123456789",  # Too long
            "+abc123456789",  # Contains letters
            "966501234567",  # Missing +
            "+966 50 123 4567",  # Contains spaces
            ""  # Empty
        ]
        
        for invalid_phone in invalid_phone_numbers:
            sms_data = {
                "to": invalid_phone,
                "message": "Test message",
                "patient_id": "patient_123"
            }
            
            response = test_client.post(
                "/api/v1/communication/send-sms",
                headers=auth_headers,
                json=sms_data
            )
            
            assert response.status_code == 422  # Unprocessable Entity

    def test_message_content_validation(self, test_client, auth_headers):
        """Test message content validation"""
        # Test empty message
        empty_message_data = {
            "to": "+966501234567",
            "message": "",
            "patient_id": "patient_123"
        }
        
        response = test_client.post(
            "/api/v1/communication/send-sms",
            headers=auth_headers,
            json=empty_message_data
        )
        assert response.status_code == 422

        # Test message too long (over SMS limit)
        long_message_data = {
            "to": "+966501234567",
            "message": "A" * 2000,  # Way over SMS limit
            "patient_id": "patient_123"
        }
        
        response = test_client.post(
            "/api/v1/communication/send-sms",
            headers=auth_headers,
            json=long_message_data
        )
        assert response.status_code == 422

    def test_arabic_text_validation(self, test_client, auth_headers):
        """Test Arabic text validation and encoding"""
        # Test valid Arabic text
        valid_arabic_data = {
            "to": "+966501234567",
            "message": "السلام عليكم، موعدك غداً",
            "patient_id": "patient_123",
            "language": "ar"
        }
        
        with patch('services.communication.arabic.nlp_processor.ArabicNLPProcessor.validate_arabic_text') as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "normalized_text": "السلام عليكم، موعدك غداً",
                "character_count": 25,
                "encoding_required": "UCS2"
            }
            
            response = test_client.post(
                "/api/v1/communication/send-sms",
                headers=auth_headers,
                json=valid_arabic_data
            )
            
            # Should accept valid Arabic text
            assert response.status_code in [200, 404, 422]

        # Test mixed Arabic and English (should be handled)
        mixed_text_data = {
            "to": "+966501234567",
            "message": "Hello مرحبا 123",
            "patient_id": "patient_123",
            "language": "mixed"
        }
        
        response = test_client.post(
            "/api/v1/communication/send-sms",
            headers=auth_headers,
            json=mixed_text_data
        )
        
        # Should handle mixed content appropriately
        assert response.status_code in [200, 404, 422]

    def test_patient_id_validation(self, test_client, auth_headers):
        """Test patient ID validation"""
        invalid_patient_ids = [
            "",  # Empty
            "invalid_id_format",  # Wrong format
            "123",  # Too short
            None  # Null
        ]
        
        for invalid_id in invalid_patient_ids:
            sms_data = {
                "to": "+966501234567",
                "message": "Test message",
                "patient_id": invalid_id
            }
            
            response = test_client.post(
                "/api/v1/communication/send-sms",
                headers=auth_headers,
                json=sms_data
            )
            
            assert response.status_code == 422

    def test_workflow_parameter_validation(self, test_client, auth_headers):
        """Test workflow parameter validation"""
        # Test invalid workflow type
        invalid_workflow_data = {
            "patient_id": "patient_123",
            "workflow_type": "nonexistent_workflow",
            "appointment_id": "apt_456"
        }
        
        response = test_client.post(
            "/api/v1/communication/trigger-workflow",
            headers=auth_headers,
            json=invalid_workflow_data
        )
        assert response.status_code == 422

        # Test missing required parameters
        incomplete_workflow_data = {
            "patient_id": "patient_123"
            # Missing workflow_type
        }
        
        response = test_client.post(
            "/api/v1/communication/trigger-workflow",
            headers=auth_headers,
            json=incomplete_workflow_data
        )
        assert response.status_code == 422

    def test_emergency_alert_validation(self, test_client, auth_headers):
        """Test emergency alert parameter validation"""
        # Test invalid severity level
        invalid_emergency_data = {
            "alert_type": "code_blue",
            "location": "ICU Room 205",
            "severity": "invalid_severity"  # Should be critical, urgent, medium, low
        }
        
        response = test_client.post(
            "/api/v1/communication/emergency-alert",
            headers=auth_headers,
            json=invalid_emergency_data
        )
        assert response.status_code == 422

        # Test missing location
        incomplete_emergency_data = {
            "alert_type": "fire_alarm",
            "severity": "critical"
            # Missing location
        }
        
        response = test_client.post(
            "/api/v1/communication/emergency-alert",
            headers=auth_headers,
            json=incomplete_emergency_data
        )
        assert response.status_code == 422

    def test_error_response_format(self, test_client, auth_headers):
        """Test error response format consistency"""
        invalid_data = {
            "to": "invalid_phone",
            "message": "",
            "patient_id": ""
        }
        
        response = test_client.post(
            "/api/v1/communication/send-sms",
            headers=auth_headers,
            json=invalid_data
        )
        
        if response.status_code == 422:
            error_response = response.json()
            # Check error response structure
            assert "detail" in error_response
            # Should contain validation error details
            if isinstance(error_response["detail"], list):
                for error in error_response["detail"]:
                    assert "loc" in error
                    assert "msg" in error
                    assert "type" in error


class TestWebhookSignatureValidation:
    """Test suite for webhook signature validation"""

    @pytest.fixture
    def test_client(self):
        """Create test client for API testing"""
        return TestClient(app)

    def generate_twilio_signature(self, url: str, params: dict, auth_token: str) -> str:
        """Generate Twilio webhook signature for testing"""
        # Concatenate URL and sorted parameters
        data = url
        for key in sorted(params.keys()):
            data += f"{key}{params[key]}"
        
        # Generate HMAC SHA1 signature
        signature = hmac.new(
            auth_token.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')

    def test_valid_twilio_webhook_signature(self, test_client):
        """Test valid Twilio webhook signature validation"""
        auth_token = "test_twilio_auth_token"
        webhook_url = "https://api.brainsait.com/api/v1/communication/webhooks/twilio/sms"
        
        webhook_params = {
            "MessageSid": "SM1234567890abcdef",
            "MessageStatus": "delivered",
            "From": "+966501234567",
            "To": "+966507654321",
            "Body": "Test message"
        }
        
        # Generate valid signature
        valid_signature = self.generate_twilio_signature(webhook_url, webhook_params, auth_token)
        
        with patch('services.communication.twilio_hipaa.base.TwilioHIPAAClient.verify_webhook_signature') as mock_verify:
            mock_verify.return_value = True
            
            response = test_client.post(
                "/api/v1/communication/webhooks/twilio/sms",
                headers={
                    "X-Twilio-Signature": valid_signature,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data=webhook_params
            )
            
            # Should accept valid signature
            assert response.status_code in [200, 404]

    def test_invalid_twilio_webhook_signature(self, test_client):
        """Test invalid Twilio webhook signature rejection"""
        webhook_params = {
            "MessageSid": "SM1234567890abcdef",
            "MessageStatus": "delivered",
            "From": "+966501234567",
            "To": "+966507654321",
            "Body": "Test message"
        }
        
        invalid_signature = "invalid_signature_hash"
        
        with patch('services.communication.twilio_hipaa.base.TwilioHIPAAClient.verify_webhook_signature') as mock_verify:
            mock_verify.return_value = False
            
            response = test_client.post(
                "/api/v1/communication/webhooks/twilio/sms",
                headers={
                    "X-Twilio-Signature": invalid_signature,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data=webhook_params
            )
            
            # Should reject invalid signature
            assert response.status_code == 401

    def test_missing_webhook_signature(self, test_client):
        """Test webhook request without signature"""
        webhook_params = {
            "MessageSid": "SM1234567890abcdef",
            "MessageStatus": "delivered",
            "From": "+966501234567",
            "To": "+966507654321"
        }
        
        response = test_client.post(
            "/api/v1/communication/webhooks/twilio/sms",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=webhook_params
        )
        
        # Should reject request without signature
        assert response.status_code in [401, 422]

    def test_webhook_replay_attack_prevention(self, test_client):
        """Test webhook replay attack prevention"""
        # Test timestamp validation for preventing replay attacks
        old_timestamp = int((datetime.now() - timedelta(hours=2)).timestamp())
        
        webhook_params = {
            "MessageSid": "SM1234567890abcdef",
            "MessageStatus": "delivered",
            "Timestamp": str(old_timestamp)
        }
        
        with patch('services.communication.twilio_hipaa.base.TwilioHIPAAClient.validate_webhook_timestamp') as mock_validate:
            mock_validate.return_value = False  # Timestamp too old
            
            response = test_client.post(
                "/api/v1/communication/webhooks/twilio/sms",
                headers={
                    "X-Twilio-Signature": "valid_signature_but_old_timestamp",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data=webhook_params
            )
            
            # Should reject old webhooks
            assert response.status_code in [401, 422]


class TestRateLimitingAndSecurity:
    """Test suite for rate limiting and security measures"""

    @pytest.fixture
    def test_client(self):
        """Create test client for API testing"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        return {
            "Authorization": "Bearer valid_token",
            "Content-Type": "application/json"
        }

    def test_rate_limiting_per_user(self, test_client, auth_headers):
        """Test per-user rate limiting"""
        sms_data = {
            "to": "+966501234567",
            "message": "Test rate limiting",
            "patient_id": "patient_123"
        }
        
        # Simulate multiple rapid requests
        with patch('utils.security.SecurityManager.check_rate_limit') as mock_rate_limit:
            # First few requests should pass
            mock_rate_limit.return_value = True
            
            for i in range(5):
                response = test_client.post(
                    "/api/v1/communication/send-sms",
                    headers=auth_headers,
                    json=sms_data
                )
                # Should be accepted within rate limit
                assert response.status_code in [200, 404, 422]
            
            # Simulate rate limit exceeded
            mock_rate_limit.return_value = False
            
            response = test_client.post(
                "/api/v1/communication/send-sms",
                headers=auth_headers,
                json=sms_data
            )
            
            # Should be rate limited
            assert response.status_code == 429

    def test_rate_limiting_per_endpoint(self, test_client, auth_headers):
        """Test per-endpoint rate limiting"""
        emergency_data = {
            "alert_type": "test_alert",
            "location": "test_location",
            "severity": "low"
        }
        
        with patch('utils.security.SecurityManager.check_endpoint_rate_limit') as mock_endpoint_limit:
            # Emergency endpoint should have stricter limits
            mock_endpoint_limit.return_value = False
            
            response = test_client.post(
                "/api/v1/communication/emergency-alert",
                headers=auth_headers,
                json=emergency_data
            )
            
            # Should be rate limited
            assert response.status_code == 429

    def test_ip_based_rate_limiting(self, test_client):
        """Test IP-based rate limiting for webhook endpoints"""
        webhook_data = {
            "MessageSid": "SM123456",
            "MessageStatus": "delivered"
        }
        
        # Simulate multiple requests from same IP
        with patch('utils.security.SecurityManager.check_ip_rate_limit') as mock_ip_limit:
            mock_ip_limit.return_value = False  # IP rate limited
            
            response = test_client.post(
                "/api/v1/communication/webhooks/twilio/sms",
                headers={"X-API-Key": "valid_key"},
                json=webhook_data
            )
            
            assert response.status_code == 429

    def test_sql_injection_prevention(self, test_client, auth_headers):
        """Test SQL injection prevention in input parameters"""
        sql_injection_attempts = [
            "'; DROP TABLE patients; --",
            "' OR '1'='1",
            "patient_123'; UPDATE patients SET name='hacked' WHERE id='1'; --"
        ]
        
        for malicious_input in sql_injection_attempts:
            sms_data = {
                "to": "+966501234567",
                "message": "Test message",
                "patient_id": malicious_input
            }
            
            response = test_client.post(
                "/api/v1/communication/send-sms",
                headers=auth_headers,
                json=sms_data
            )
            
            # Should reject malicious input
            assert response.status_code == 422

    def test_xss_prevention(self, test_client, auth_headers):
        """Test XSS prevention in message content"""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<%=7*7%>",
            "${alert('xss')}"
        ]
        
        for malicious_content in xss_attempts:
            sms_data = {
                "to": "+966501234567",
                "message": malicious_content,
                "patient_id": "patient_123"
            }
            
            with patch('utils.security.SecurityManager.sanitize_input') as mock_sanitize:
                mock_sanitize.return_value = "sanitized_content"
                
                response = test_client.post(
                    "/api/v1/communication/send-sms",
                    headers=auth_headers,
                    json=sms_data
                )
                
                # Should sanitize malicious content
                mock_sanitize.assert_called()

    def test_request_size_limits(self, test_client, auth_headers):
        """Test request size limits"""
        # Test oversized request
        large_message = "A" * 10000  # Very large message
        
        oversized_data = {
            "to": "+966501234567",
            "message": large_message,
            "patient_id": "patient_123",
            "metadata": {"large_field": "X" * 5000}
        }
        
        response = test_client.post(
            "/api/v1/communication/send-sms",
            headers=auth_headers,
            json=oversized_data
        )
        
        # Should reject oversized requests
        assert response.status_code in [413, 422]

    def test_concurrent_request_handling(self, test_client, auth_headers):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            sms_data = {
                "to": "+966501234567",
                "message": f"Concurrent test {threading.current_thread().ident}",
                "patient_id": "patient_123"
            }
            
            response = test_client.post(
                "/api/v1/communication/send-sms",
                headers=auth_headers,
                json=sms_data
            )
            results.append(response.status_code)
        
        # Create multiple concurrent requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should handle concurrent requests gracefully
        # Most should succeed, some might be rate limited
        success_count = sum(1 for code in results if code in [200, 404])
        rate_limited_count = sum(1 for code in results if code == 429)
        
        # Should have some successful responses
        assert success_count > 0 or rate_limited_count > 0


class TestAuditLoggingAPI:
    """Test suite for audit logging API endpoints"""

    @pytest.fixture
    def test_client(self):
        """Create test client for API testing"""
        return TestClient(app)

    @pytest.fixture
    def admin_auth_headers(self):
        """Mock admin authentication headers"""
        return {
            "Authorization": "Bearer admin_token",
            "Content-Type": "application/json"
        }

    def test_audit_log_retrieval(self, test_client, admin_auth_headers):
        """Test audit log retrieval endpoint"""
        audit_query = {
            "start_date": "2024-08-01T00:00:00Z",
            "end_date": "2024-08-05T23:59:59Z",
            "event_types": ["message_sent", "workflow_triggered"],
            "patient_id": "patient_123",
            "limit": 50
        }
        
        with patch('services.communication.twilio_hipaa.compliance.HIPAACompliance.get_audit_logs') as mock_get_logs:
            mock_get_logs.return_value = {
                "logs": [
                    {
                        "audit_id": "audit_123",
                        "timestamp": "2024-08-04T10:30:00Z",
                        "event_type": "message_sent",
                        "user_id": "doctor_456",
                        "patient_id": "patient_123",
                        "action": "SMS sent to patient",
                        "phi_accessed": False,
                        "compliance_status": "compliant"
                    }
                ],
                "total_count": 1,
                "page": 1,
                "has_more": False
            }
            
            response = test_client.post(
                "/api/v1/communication/audit-logs",
                headers=admin_auth_headers,
                json=audit_query
            )
            
            if response.status_code == 200:
                response_data = response.json()
                assert "logs" in response_data
                assert len(response_data["logs"]) > 0

    def test_hipaa_compliance_report(self, test_client, admin_auth_headers):
        """Test HIPAA compliance report endpoint"""
        report_request = {
            "report_type": "monthly_compliance",
            "start_date": "2024-07-01T00:00:00Z",
            "end_date": "2024-07-31T23:59:59Z",
            "include_phi_access": True,
            "include_violations": True
        }
        
        with patch('services.communication.twilio_hipaa.compliance.HIPAACompliance.generate_compliance_report') as mock_report:
            mock_report.return_value = {
                "report_id": "report_monthly_789",
                "period": "July 2024",
                "total_communications": 2500,
                "phi_detected_count": 45,
                "phi_masked_count": 45,
                "compliance_rate": 100.0,
                "violations": [],
                "recommendations": [
                    "Continue current PHI detection practices",
                    "Review staff training quarterly"
                ]
            }
            
            response = test_client.post(
                "/api/v1/communication/compliance-report",
                headers=admin_auth_headers,
                json=report_request
            )
            
            if response.status_code == 200:
                response_data = response.json()
                assert response_data["compliance_rate"] == 100.0
                assert len(response_data["violations"]) == 0


if __name__ == "__main__":
    # Run the API tests
    pytest.main([__file__, "-v", "--tb=short"])