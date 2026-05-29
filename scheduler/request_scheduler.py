"""
APScheduler-based scheduler for sending periodic API requests to ServiceNow.
"""

import time
import logging
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RequestSchedulerThread(QThread):
    """QThread-based scheduler for API requests."""

    # Signals
    status_updated = pyqtSignal(str, str)  # message, status_type

    def __init__(self, api_client, form_name, fields, schedule_type="minutely", interval=1):
        """
        Initialize the scheduler.

        Args:
            api_client: ServiceNowClient instance
            form_name: ServiceNow table name
            fields: Dictionary of fields to send with each request
            schedule_type: 'minutely', 'hourly', or 'daily'
            interval: Interval value
        """
        super().__init__()

        self.api_client = api_client
        self.form_name = form_name
        self.fields = fields
        self.schedule_type = schedule_type.lower()
        self.interval = interval

        self.scheduler = BackgroundScheduler()
        self.running = True
        self.request_count = 0

    def run(self):
        """Run the scheduler in QThread."""
        try:
            # Configure the scheduler
            self._configure_scheduler()

            # Start scheduler
            self.scheduler.start()

            self.status_updated.emit(
                f"Scheduler started: Every {self.interval} {self.schedule_type}",
                "running",
            )

            logger.info(f"Scheduler started: {self.schedule_type} interval of {self.interval}")

            # Keep thread alive until stop is called
            while self.running:
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
            self.status_updated.emit(f"Scheduler error: {str(e)}", "error")

        finally:
            self._cleanup()

    def _configure_scheduler(self):
        """Configure APScheduler with appropriate trigger."""
        # Map schedule types to kwargs
        trigger_kwargs = {}

        if self.schedule_type == "minutely":
            trigger_kwargs = {"minutes": self.interval}
        elif self.schedule_type == "hourly":
            trigger_kwargs = {"hours": self.interval}
        elif self.schedule_type == "daily":
            trigger_kwargs = {"days": self.interval}
        else:
            trigger_kwargs = {"minutes": 1}

        # Add job to scheduler
        self.scheduler.add_job(
            self._send_request_job,
            "interval",
            **trigger_kwargs,
            id="servicenow_request_job",
            name=f"ServiceNow {self.form_name} Request",
            replace_existing=True,
        )

    def _send_request_job(self):
        """Job function that sends the API request."""
        try:
            self.request_count += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            logger.info(f"[{timestamp}] Sending request #{self.request_count}...")

            # Send request
            response = self.api_client.send_request(self.form_name, self.fields)

            if response.get("success"):
                message = f"✓ Request #{self.request_count} successful at {timestamp}. ID: {response.get('id')}"
                logger.info(message)
                self.status_updated.emit(message, "success")
            else:
                message = f"✗ Request #{self.request_count} failed: {response.get('message', 'Unknown error')}"
                logger.warning(message)
                self.status_updated.emit(message, "error")

        except Exception as e:
            message = f"✗ Exception during request: {str(e)}"
            logger.error(message)
            self.status_updated.emit(message, "error")

    def stop_scheduler(self):
        """Stop the scheduler."""
        try:
            self.running = False
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")

        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")

    def _cleanup(self):
        """Clean up resources."""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
