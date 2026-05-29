"""
Configuration tests for the application.
"""

import pytest
from api.servicenow_client import ServiceNowClient


class TestIntegration:
    """Integration tests for the application."""
    
    def test_servicenow_client_workflow(self, servicenow_credentials, test_fields):
        """Test basic ServiceNowClient workflow."""
        client = ServiceNowClient()
        
        # Set credentials
        client.set_credentials(**servicenow_credentials)
        
        # Verify credentials are set
        assert client.url == servicenow_credentials["url"]
        assert client.username == servicenow_credentials["username"]
        assert client.password == servicenow_credentials["password"]
    
    def test_ca_certificate_workflow(self, temp_ca_cert, servicenow_credentials):
        """Test CA certificate workflow."""
        client = ServiceNowClient()
        
        # Set credentials with CA cert
        servicenow_credentials["ca_cert_path"] = temp_ca_cert
        client.set_credentials(**servicenow_credentials)
        
        assert client.ca_cert_path == temp_ca_cert
