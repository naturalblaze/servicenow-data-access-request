"""
Unit tests for request scheduler.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from scheduler.request_scheduler import RequestSchedulerThread


class TestRequestSchedulerThreadInit:
    """Test RequestSchedulerThread initialization."""
    
    def test_init_with_minutely_schedule(self):
        """Test scheduler initialization with minutely schedule."""
        mock_client = Mock()
        
        scheduler = RequestSchedulerThread(
            api_client=mock_client,
            form_name="incident",
            fields={"short_description": "test"},
            schedule_type="minutely",
            interval=5
        )
        
        assert scheduler.api_client == mock_client
        assert scheduler.form_name == "incident"
        assert scheduler.fields == {"short_description": "test"}
        assert scheduler.schedule_type == "minutely"
        assert scheduler.interval == 5
        assert scheduler.request_count == 0
        assert scheduler.running is True
    
    def test_init_normalizes_schedule_type(self):
        """Test that schedule type is normalized to lowercase."""
        mock_client = Mock()
        
        scheduler = RequestSchedulerThread(
            api_client=mock_client,
            form_name="incident",
            fields={},
            schedule_type="DAILY",
            interval=1
        )
        
        assert scheduler.schedule_type == "daily"
    
    def test_init_different_schedule_types(self):
        """Test initialization with different schedule types."""
        mock_client = Mock()
        
        for schedule_type in ["minutely", "hourly", "daily"]:
            scheduler = RequestSchedulerThread(
                api_client=mock_client,
                form_name="incident",
                fields={},
                schedule_type=schedule_type,
                interval=1
            )
            assert scheduler.schedule_type == schedule_type


class TestRequestSchedulerSignals:
    """Test RequestSchedulerThread signals."""
    
    def test_status_updated_signal_exists(self):
        """Test that status_updated signal is defined."""
        mock_client = Mock()
        scheduler = RequestSchedulerThread(
            api_client=mock_client,
            form_name="incident",
            fields={},
            schedule_type="minutely",
            interval=1
        )
        
        # Check signal exists
        assert hasattr(scheduler, 'status_updated')


class TestConfigureScheduler:
    """Test _configure_scheduler method."""
    
    def test_configure_scheduler_minutely(self):
        """Test scheduler configuration for minutely interval."""
        mock_client = Mock()
        scheduler = RequestSchedulerThread(
            api_client=mock_client,
            form_name="incident",
            fields={},
            schedule_type="minutely",
            interval=5
        )
        
        scheduler._configure_scheduler()
        
        # Check that a job was added
        assert scheduler.scheduler.get_job("servicenow_request_job") is not None
    
    def test_configure_scheduler_hourly(self):
        """Test scheduler configuration for hourly interval."""
        mock_client = Mock()
        scheduler = RequestSchedulerThread(
            api_client=mock_client,
            form_name="incident",
            fields={},
            schedule_type="hourly",
            interval=2
        )
        
        scheduler._configure_scheduler()
        
        assert scheduler.scheduler.get_job("servicenow_request_job") is not None
    
    def test_configure_scheduler_daily(self):
        """Test scheduler configuration for daily interval."""
        mock_client = Mock()
        scheduler = RequestSchedulerThread(
            api_client=mock_client,
            form_name="incident",
            fields={},
            schedule_type="daily",
            interval=1
        )
        
        scheduler._configure_scheduler()
        
        assert scheduler.scheduler.get_job("servicenow_request_job") is not None


class TestSendRequestJob:
    """Test _send_request_job method."""
    
    def test_send_request_job_success(self):
        """Test successful request job."""
        mock_client = Mock()
        mock_client.send_request.return_value = {
            "success": True,
            "id": "INC0001234",
            "message": "Success"
        }
        
        scheduler = RequestSchedulerThread(
            api_client=mock_client,
            form_name="incident",
            fields={"short_description": "test"},
            schedule_type="minutely",
            interval=1
        )
        
        scheduler._send_request_job()
        
        assert scheduler.request_count == 1
        mock_client.send_request.assert_called_once_with(
            "incident",
            {"short_description": "test"}
        )
    
    def test_send_request_job_failure(self):
        """Test failed request job."""
        mock_client = Mock()
        mock_client.send_request.return_value = {
            "success": False,
            "message": "Authentication failed"
        }
        
        scheduler = RequestSchedulerThread(
            api_client=mock_client,
            form_name="incident",
            fields={},
            schedule_type="minutely",
            interval=1
        )
        
        scheduler._send_request_job()
        
        assert scheduler.request_count == 1
    
    def test_send_request_job_exception(self):
        """Test request job with exception."""
        mock_client = Mock()
        mock_client.send_request.side_effect = Exception("Connection error")
        
        scheduler = RequestSchedulerThread(
            api_client=mock_client,
            form_name="incident",
            fields={},
            schedule_type="minutely",
            interval=1
        )
        
        # Should not raise exception
        scheduler._send_request_job()
        
        assert scheduler.request_count == 1


class TestStopScheduler:
    """Test stop_scheduler method."""
    
    def test_stop_scheduler(self):
        """Test stopping the scheduler."""
        mock_client = Mock()
        scheduler = RequestSchedulerThread(
            api_client=mock_client,
            form_name="incident",
            fields={},
            schedule_type="minutely",
            interval=1
        )
        
        scheduler._configure_scheduler()
        scheduler.scheduler.start()
        
        # Stop the scheduler
        scheduler.stop_scheduler()
        
        assert scheduler.running is False
