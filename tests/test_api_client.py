"""
Unit tests for ServiceNow API client.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import requests
from api.servicenow_client import ServiceNowClient


class TestServiceNowClientInit:
    """Test ServiceNowClient initialization."""
    
    def test_init_default_values(self):
        """Test client initializes with correct default values."""
        client = ServiceNowClient()
        assert client.url is None
        assert client.username is None
        assert client.password is None
        assert client.ca_cert_path is None
        assert client.timeout == 30
    
    def test_timeout_value(self):
        """Test timeout is set to 30 seconds."""
        client = ServiceNowClient()
        assert client.timeout == 30


class TestSetCredentials:
    """Test set_credentials method."""
    
    def test_set_credentials_basic(self):
        """Test setting basic credentials without CA certificate."""
        client = ServiceNowClient()
        client.set_credentials(
            url="https://dev12345.service-now.com",
            username="test_user",
            password="test_pass"
        )
        
        assert client.url == "https://dev12345.service-now.com"
        assert client.username == "test_user"
        assert client.password == "test_pass"
        assert client.ca_cert_path is None
    
    def test_set_credentials_removes_trailing_slash(self):
        """Test that trailing slash is removed from URL."""
        client = ServiceNowClient()
        client.set_credentials(
            url="https://dev12345.service-now.com/",
            username="test_user",
            password="test_pass"
        )
        
        assert client.url == "https://dev12345.service-now.com"
    
    def test_set_credentials_with_valid_ca_cert(self):
        """Test setting credentials with valid CA certificate file."""
        client = ServiceNowClient()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
            f.write("-----BEGIN CERTIFICATE-----\n")
            f.write("FAKE_CERT_DATA\n")
            f.write("-----END CERTIFICATE-----\n")
            cert_path = f.name
        
        try:
            client.set_credentials(
                url="https://dev12345.service-now.com",
                username="test_user",
                password="test_pass",
                ca_cert_path=cert_path
            )
            
            assert client.ca_cert_path == cert_path
        finally:
            os.unlink(cert_path)
    
    def test_set_credentials_with_invalid_ca_cert(self):
        """Test that invalid CA certificate path raises ValueError."""
        client = ServiceNowClient()
        
        with pytest.raises(ValueError) as exc_info:
            client.set_credentials(
                url="https://dev12345.service-now.com",
                username="test_user",
                password="test_pass",
                ca_cert_path="/nonexistent/path/to/cert.pem"
            )
        
        assert "CA certificate file not found" in str(exc_info.value)


class TestSendRequest:
    """Test send_request method."""
    
    def test_send_request_missing_credentials(self):
        """Test send_request without credentials."""
        client = ServiceNowClient()
        response = client.send_request("incident", {"short_description": "test"})
        
        assert response["success"] is False
        assert "Credentials not set" in response["message"]
    
    @patch('requests.post')
    def test_send_request_success(self, mock_post):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "result": {
                "sys_id": "12345",
                "short_description": "test"
            }
        }
        mock_post.return_value = mock_response
        
        client = ServiceNowClient()
        client.set_credentials(
            url="https://dev12345.service-now.com",
            username="test_user",
            password="test_pass"
        )
        
        response = client.send_request("incident", {"short_description": "test"})
        
        assert response["success"] is True
        assert response["id"] == "12345"
        assert "Successfully created" in response["message"]
        
        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"] == {"short_description": "test"}
        assert call_args[1]["verify"] is True
    
    @patch('requests.post')
    def test_send_request_with_custom_ca_cert(self, mock_post):
        """Test API request with custom CA certificate."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"result": {"sys_id": "12345"}}
        mock_post.return_value = mock_response
        
        client = ServiceNowClient()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
            f.write("FAKE_CERT")
            cert_path = f.name
        
        try:
            client.set_credentials(
                url="https://dev12345.service-now.com",
                username="test_user",
                password="test_pass",
                ca_cert_path=cert_path
            )
            
            response = client.send_request("incident", {"test": "data"})
            
            assert response["success"] is True
            # Verify custom CA cert was used
            call_args = mock_post.call_args
            assert call_args[1]["verify"] == cert_path
        finally:
            os.unlink(cert_path)
    
    @patch('requests.post')
    def test_send_request_authentication_error(self, mock_post):
        """Test API request with authentication failure."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        client = ServiceNowClient()
        client.set_credentials(
            url="https://dev12345.service-now.com",
            username="bad_user",
            password="bad_pass"
        )
        
        response = client.send_request("incident", {"test": "data"})
        
        assert response["success"] is False
        assert "Authentication failed" in response["message"]
    
    @patch('requests.post')
    def test_send_request_table_not_found(self, mock_post):
        """Test API request with table not found error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response
        
        client = ServiceNowClient()
        client.set_credentials(
            url="https://dev12345.service-now.com",
            username="test_user",
            password="test_pass"
        )
        
        response = client.send_request("invalid_table", {"test": "data"})
        
        assert response["success"] is False
        assert "not found" in response["message"]
    
    @patch('requests.post')
    def test_send_request_connection_error(self, mock_post):
        """Test API request with connection error."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        client = ServiceNowClient()
        client.set_credentials(
            url="https://invalid.service-now.com",
            username="test_user",
            password="test_pass"
        )
        
        response = client.send_request("incident", {"test": "data"})
        
        assert response["success"] is False
        assert "Connection error" in response["message"]
    
    @patch('requests.post')
    def test_send_request_timeout(self, mock_post):
        """Test API request with timeout."""
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        client = ServiceNowClient()
        client.set_credentials(
            url="https://dev12345.service-now.com",
            username="test_user",
            password="test_pass"
        )
        
        response = client.send_request("incident", {"test": "data"})
        
        assert response["success"] is False
        assert "timeout" in response["message"].lower()


class TestTestConnection:
    """Test test_connection method."""
    
    def test_test_connection_missing_credentials(self):
        """Test connection test without credentials."""
        client = ServiceNowClient()
        response = client.test_connection()
        
        assert response["success"] is False
        assert "Credentials not set" in response["message"]
    
    @patch('requests.get')
    def test_test_connection_success(self, mock_get):
        """Test successful connection test."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = ServiceNowClient()
        client.set_credentials(
            url="https://dev12345.service-now.com",
            username="test_user",
            password="test_pass"
        )
        
        response = client.test_connection()
        
        assert response["success"] is True
        assert "Connection successful" in response["message"]
    
    @patch('requests.get')
    def test_test_connection_auth_failure(self, mock_get):
        """Test connection test with authentication failure."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        client = ServiceNowClient()
        client.set_credentials(
            url="https://dev12345.service-now.com",
            username="bad_user",
            password="bad_pass"
        )
        
        response = client.test_connection()
        
        assert response["success"] is False
        assert "Authentication failed" in response["message"]
    
    @patch('requests.get')
    def test_test_connection_with_custom_ca_cert(self, mock_get):
        """Test connection with custom CA certificate."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = ServiceNowClient()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
            f.write("FAKE_CERT")
            cert_path = f.name
        
        try:
            client.set_credentials(
                url="https://dev12345.service-now.com",
                username="test_user",
                password="test_pass",
                ca_cert_path=cert_path
            )
            
            response = client.test_connection()
            
            assert response["success"] is True
            # Verify custom CA cert was used
            call_args = mock_get.call_args
            assert call_args[1]["verify"] == cert_path
        finally:
            os.unlink(cert_path)
