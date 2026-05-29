"""
Fixtures for testing.
"""

import pytest
import tempfile
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pytest_configure(config):
    """Pytest configuration hook."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )


@pytest.fixture
def temp_ca_cert():
    """Fixture that provides a temporary CA certificate file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
        f.write("-----BEGIN CERTIFICATE-----\n")
        f.write("MIIDXTCCAkWgAwIBAgIJAJC1/iNAZwqDMA0GCSqGSIb3DQEBBQUAMEUxCzAJBgNV\n")
        f.write("-----END CERTIFICATE-----\n")
        cert_path = f.name
    
    yield cert_path
    
    # Cleanup
    if os.path.exists(cert_path):
        os.unlink(cert_path)


@pytest.fixture
def mock_api_client():
    """Fixture that provides a mock API client."""
    from unittest.mock import Mock
    
    client = Mock()
    client.url = "https://dev12345.service-now.com"
    client.username = "test_user"
    client.password = "test_pass"
    client.ca_cert_path = None
    
    return client


@pytest.fixture
def servicenow_credentials():
    """Fixture that provides test ServiceNow credentials."""
    return {
        "url": "https://dev12345.service-now.com",
        "username": "test_user",
        "password": "test_pass"
    }


@pytest.fixture
def test_fields():
    """Fixture that provides test request fields."""
    return {
        "short_description": "Test incident",
        "description": "This is a test incident",
        "priority": "3"
    }
