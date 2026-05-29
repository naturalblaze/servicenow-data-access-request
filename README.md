# ServiceNow Data Access Request Application

A PyQt5-based GUI application for sending scheduled API requests to ServiceNow forms/tables. This tool allows you to configure and automate periodic data submissions to ServiceNow instances.

## Features

- **GUI Interface**: User-friendly PyQt5 interface for configuration

- **ServiceNow Integration**: Sends REST API requests to ServiceNow tables

- **Secure Authentication**: Masked password input, HTTP Basic Auth support

- **Custom SSL Certificates**: Optional custom CA certificate support for HTTPS connections

- **Customizable Fields**: Add/delete key-value pairs for flexible data submission

- **Advanced Scheduling**: 

  - Minutely, hourly, or daily execution

  - Configurable intervals using APScheduler

- **Start/Stop Control**: Easy management of scheduled requests

- **Test Requests**: Send test requests before scheduling to verify configuration

- **Status Monitoring**: Real-time status updates and request logs

- **Comprehensive Testing**: Unit tests with pytest and code coverage reporting

## Requirements

- Python 3.12+

- PyQt5

- Requests

- APScheduler

## Installation

1. Clone or download this repository

2. Create Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```


2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
source .venv/bin/activate
python main.py
```

### Configuration Steps

1. **ServiceNow Connection**

   - Enter your ServiceNow instance URL (e.g., `https://dev12345.service-now.com`)
   - Enter your username and password

   - Specify the table name (e.g., `incident`, `change_request`, or custom table)

   - (Optional) Select a custom CA certificate file for HTTPS connections with custom/self-signed certificates

     - Click "Browse..." next to "SSL CA Certificate"

     - Select a `.pem`, `.crt`, or `.cer` certificate file

     - This is optional; leave blank to use system default certificates

2. **Request Fields**

   - Click "Add Field" to add key-value pairs

   - Enter field names (keys) and values

   - Remove fields as needed

3. **Schedule Configuration**

   - Select interval type: Minutely, Hourly, or Daily

   - Set the frequency (how many minutes/hours/days between requests)

4. **Testing**

   - Click "Send Test Request" to verify your configuration

   - Check the status message for success or error details

5. **Start Scheduling**

   - Click "Start Scheduler" to begin automatic requests

   - Click "Stop Scheduler" to stop the scheduled requests

## ServiceNow API Details

### Endpoint Format
```
POST https://{instance}.service-now.com/api/now/table/{table_name}
```

### Authentication
- Uses HTTP Basic Authentication
- Provide valid ServiceNow user credentials

### Request Payload
The application sends field data as JSON:
```json
{
  "field_name": "field_value",
  "another_field": "another_value"
}
```

### Response
Successful responses return:
```json
{
  "result": {
    "sys_id": "record_id",
    ...other fields...
  }
}
```

## Project Structure

```
servicenow-data-access-request/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
├── Makefile               # Development commands
├── setup.cfg              # Test and tool configuration
├── pytest.ini             # Pytest configuration
├── gui/
│   ├── __init__.py
│   ├── main_window.py      # Main GUI window
│   └── widgets/
│       ├── __init__.py
│       └── field_widget.py # Custom field widget
├── api/
│   ├── __init__.py
│   └── servicenow_client.py # ServiceNow API client
├── scheduler/
│   ├── __init__.py
│   └── request_scheduler.py # APScheduler integration
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures
│   ├── test_api_client.py   # API client tests
│   ├── test_scheduler.py    # Scheduler tests
│   └── test_integration.py  # Integration tests
└── README.md               # This file
```

## Testing

The project includes comprehensive unit tests using pytest with coverage reporting.

### Installation for Testing

```bash
# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Tests

Using the Makefile (recommended):

```bash
# Run all tests
make test

# Run tests with coverage report
make test-cov

# Generate HTML coverage report
make test-cov-html
```

Or using pytest directly:

```bash
# Run all tests with verbose output
.venv/bin/pytest tests/ -v

# Run specific test file
.venv/bin/pytest tests/test_api_client.py -v

# Run with coverage
.venv/bin/pytest tests/ -v --cov=. --cov-report=term-missing

# Generate HTML coverage report
.venv/bin/pytest tests/ -v --cov=. --cov-report=html
```

### Test Coverage

The test suite covers:

- **API Client Tests** (`test_api_client.py`)
  - Client initialization
  - Credential setting with and without CA certificates
  - SSL certificate validation
  - Successful API requests
  - Authentication failures
  - Connection errors and timeouts
  - Custom CA certificate usage

- **Scheduler Tests** (`test_scheduler.py`)
  - Scheduler initialization with different intervals
  - Schedule type configuration
  - Request job execution
  - Error handling in scheduled requests
  - Scheduler startup and shutdown

- **Integration Tests** (`test_integration.py`)
  - End-to-end workflows
  - Credential and CA certificate workflows

### Code Quality Tools

The development setup includes:

```bash
# Format code with black
make format

# Run linters (flake8, mypy)
make lint

# Clean up temporary files
make clean
```

## Troubleshooting

### Connection Error
- Verify the ServiceNow URL is correct
- Check network connectivity
- Ensure firewall allows access to ServiceNow instance

### Authentication Failed
- Confirm username and password are correct
- Verify user has API access permissions
- Check if account is locked

### Table Not Found
- Verify the table name is correct (case-sensitive in some instances)
- Ensure user has access to the table
- Check if it's a custom table with correct naming

### No Requests Sending
- Verify at least one field is configured
- Check the scheduler status in the Status panel
- Review error messages in the status display
- Click "Send Test Request" to verify connectivity

### SSL Certificate Errors
- If you get SSL verification errors, you may need a custom CA certificate
- Ensure the certificate file is in PEM format (.pem, .crt, or .cer)
- The certificate path must be readable by the application
- Test with the "Send Test Request" button to verify the certificate works
- For self-signed certificates, ensure the certificate file contains the proper CA chain

## SSL/Certificate Configuration

### Using Custom CA Certificates

The application supports custom CA certificates for HTTPS connections. This is useful when:

- Your ServiceNow instance uses a self-signed SSL certificate
- Your organization uses an internal Certificate Authority (CA)
- You need to use a specific certificate chain

### How to Configure

1. **Obtain the CA Certificate**
   - Export the certificate from your ServiceNow instance or CA
   - Ensure it's in PEM format (.pem, .crt, or .cer)

2. **Add to Application**
   - In the GUI, locate "SSL CA Certificate" in the connection settings
   - Click "Browse..." to select the certificate file
   - Leave blank to use system default certificates

3. **Test the Configuration**
   - Click "Send Test Request" to verify the certificate works
   - If successful, you can proceed with scheduling

### Certificate File Format

The application expects PEM-formatted certificates. A typical PEM certificate looks like:

```
-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAJC1/iNAZwqDMA0GCSqGSIb3...
...base64 encoded data...
-----END CERTIFICATE-----
```

### Common Issues

- **Certificate not found**: Ensure the file path is correct and readable
- **Invalid certificate format**: Certificate must be in PEM format
- **Certificate verification failed**: The certificate may not be properly signed or in the correct chain

## Security Notes

- Credentials are only stored in memory during application runtime
- Password input is masked in the GUI
- Use HTTPS connections to ServiceNow
- Custom CA certificates are only stored during runtime and not persisted to disk
- Avoid sharing credentials or leaving the application running unattended
- For self-signed certificates, verify the certificate chain is complete and valid

## API Request Flow

1. Application collects configuration from GUI
2. Validates all required fields
3. APScheduler triggers requests at configured intervals
4. API client sends HTTP POST request with credentials
5. Response is processed and logged
6. Status is displayed in GUI
7. Process repeats on schedule

## Logging

The application logs all activities to the console. For debugging, check the console output or modify logging levels in `scheduler/request_scheduler.py`.

## License

See LICENSE file for details.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review error messages in the Status panel
3. Test connectivity using "Send Test Request" button
4. Verify all configuration settings

## Future Enhancements

Potential features for future versions:
- Configuration file saving/loading
- Multiple scheduled requests
- Email notifications for failures
- Request history and analytics
- Custom headers support
- Retry logic with exponential backoff
- Database persistence for request history
- Advanced filtering and query support
