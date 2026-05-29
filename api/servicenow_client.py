"""
ServiceNow API client for sending requests to ServiceNow forms/tables.
"""

import requests
import os
from requests.auth import HTTPBasicAuth


class ServiceNowClient:
    """Client for interacting with ServiceNow API."""

    def __init__(self):
        self.url = None
        self.username = None
        self.password = None
        self.ca_cert_path = None
        self.timeout = 30

    def set_credentials(self, url, username, password, ca_cert_path=None):
        """
        Set credentials for ServiceNow authentication.

        Args:
            url: ServiceNow instance URL (e.g., https://dev12345.service-now.com)
            username: ServiceNow username
            password: ServiceNow password
            ca_cert_path: Optional path to custom CA certificate file

        Raises:
            ValueError: If ca_cert_path is provided but file doesn't exist
        """
        # Ensure URL ends without slash for consistency
        self.url = url.rstrip("/")
        self.username = username
        self.password = password

        # Validate CA certificate path if provided
        if ca_cert_path:
            if not os.path.isfile(ca_cert_path):
                raise ValueError(f"CA certificate file not found: {ca_cert_path}")
            self.ca_cert_path = ca_cert_path
        else:
            self.ca_cert_path = None

    def send_request(self, table_name, data):
        """
        Send a POST request to ServiceNow table.

        Args:
            table_name: Name of the ServiceNow table (e.g., 'incident')
            data: Dictionary of fields to submit

        Returns:
            Dictionary containing response data with 'success' key
        """
        if not all([self.url, self.username, self.password]):
            return {
                "success": False,
                "message": "Credentials not set. Please configure connection settings.",
            }

        try:
            # Construct API endpoint
            endpoint = f"{self.url}/api/now/table/{table_name}"

            # Prepare headers
            headers = {"Content-Type": "application/json", "Accept": "application/json"}

            # Create authentication
            auth = HTTPBasicAuth(self.username, self.password)

            # Determine SSL verification settings
            verify = self.ca_cert_path if self.ca_cert_path else True

            # Send POST request
            response = requests.post(
                endpoint,
                json=data,
                auth=auth,
                headers=headers,
                timeout=self.timeout,
                verify=verify,
            )

            # Check response status
            if response.status_code in [200, 201]:
                response_data = response.json()
                result = response_data.get("result", {})

                return {
                    "success": True,
                    "id": result.get("sys_id", "N/A"),
                    "message": f"Successfully created record in {table_name}",
                    "data": result,
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "message": "Authentication failed. Please check username and password.",
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "message": f"Table '{table_name}' not found on ServiceNow instance.",
                }
            else:
                return {
                    "success": False,
                    "message": f"Request failed with status {response.status_code}: {response.text}",
                }

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "Connection error. Please check the ServiceNow URL and network connectivity.",
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "Request timeout. ServiceNow instance is not responding.",
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}

    def test_connection(self):
        """
        Test the connection to ServiceNow instance.

        Returns:
            Dictionary with 'success' key indicating connection status
        """
        if not all([self.url, self.username, self.password]):
            return {"success": False, "message": "Credentials not set."}

        try:
            # Try to access the API
            endpoint = f"{self.url}/api/now/table/sys_user"
            auth = HTTPBasicAuth(self.username, self.password)
            headers = {"Accept": "application/json"}

            # Determine SSL verification settings
            verify = self.ca_cert_path if self.ca_cert_path else True

            response = requests.get(
                endpoint,
                auth=auth,
                headers=headers,
                timeout=self.timeout,
                verify=verify,
                params={"sysparm_limit": 1},
            )

            if response.status_code == 200:
                return {"success": True, "message": "Connection successful"}
            elif response.status_code == 401:
                return {"success": False, "message": "Authentication failed"}
            else:
                return {
                    "success": False,
                    "message": f"Connection failed: {response.status_code}",
                }

        except Exception as e:
            return {"success": False, "message": f"Connection error: {str(e)}"}
