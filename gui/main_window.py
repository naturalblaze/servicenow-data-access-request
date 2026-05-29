"""
Main window for the ServiceNow Data Access Request application.
"""

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QSpinBox,
    QComboBox,
    QGroupBox,
    QMessageBox,
    QHeaderView,
    QFileDialog,
)
from api.servicenow_client import ServiceNowClient
from scheduler.request_scheduler import RequestSchedulerThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ServiceNow Data Access Request")
        self.setGeometry(100, 100, 900, 700)

        # Initialize API client and scheduler
        self.api_client = ServiceNowClient()
        self.scheduler_thread = None

        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Connection Settings Group
        connection_group = self._create_connection_group()
        main_layout.addWidget(connection_group)

        # Fields Configuration Group
        fields_group = self._create_fields_group()
        main_layout.addWidget(fields_group)

        # Schedule Configuration Group
        schedule_group = self._create_schedule_group()
        main_layout.addWidget(schedule_group)

        # Control Buttons Group
        control_group = self._create_control_group()
        main_layout.addWidget(control_group)

        # Status Group
        status_group = self._create_status_group()
        main_layout.addWidget(status_group)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def _create_connection_group(self):
        """Create connection settings group."""
        group = QGroupBox("ServiceNow Connection")
        layout = QVBoxLayout()

        # URL Input
        url_layout = QHBoxLayout()
        url_label = QLabel("ServiceNow URL:")
        url_label.setFixedWidth(150)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://dev12345.service-now.com")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Username Input
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        username_label.setFixedWidth(150)
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # Password Input
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setFixedWidth(150)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # Form Name Input
        form_layout = QHBoxLayout()
        form_label = QLabel("Form Name/Table:")
        form_label.setFixedWidth(150)
        self.form_input = QLineEdit()
        self.form_input.setPlaceholderText("incident (or custom table name)")
        form_layout.addWidget(form_label)
        form_layout.addWidget(self.form_input)
        layout.addLayout(form_layout)

        # SSL CA Certificate Input
        ca_cert_layout = QHBoxLayout()
        ca_cert_label = QLabel("SSL CA Certificate:")
        ca_cert_label.setFixedWidth(150)
        self.ca_cert_input = QLineEdit()
        self.ca_cert_input.setPlaceholderText("(Optional) Path to CA certificate file")
        self.ca_cert_input.setReadOnly(True)
        ca_cert_browse_btn = QPushButton("Browse...")
        ca_cert_browse_btn.setMaximumWidth(80)
        ca_cert_browse_btn.clicked.connect(self._browse_ca_certificate)
        ca_cert_layout.addWidget(ca_cert_label)
        ca_cert_layout.addWidget(self.ca_cert_input)
        ca_cert_layout.addWidget(ca_cert_browse_btn)
        layout.addLayout(ca_cert_layout)

        group.setLayout(layout)
        return group

    def _create_fields_group(self):
        """Create customizable fields configuration group."""
        group = QGroupBox("Request Fields")
        layout = QVBoxLayout()

        # Fields table
        self.fields_table = QTableWidget()
        self.fields_table.setColumnCount(2)
        self.fields_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.fields_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.fields_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.fields_table)

        # Buttons for field management
        button_layout = QHBoxLayout()
        add_field_btn = QPushButton("Add Field")
        add_field_btn.clicked.connect(self._add_field)
        remove_field_btn = QPushButton("Remove Selected Field")
        remove_field_btn.clicked.connect(self._remove_field)

        button_layout.addWidget(add_field_btn)
        button_layout.addWidget(remove_field_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        group.setLayout(layout)
        return group

    def _create_schedule_group(self):
        """Create schedule configuration group."""
        group = QGroupBox("Schedule Configuration")
        layout = QVBoxLayout()

        # Schedule type
        schedule_layout = QHBoxLayout()
        schedule_label = QLabel("Schedule Interval:")
        schedule_label.setFixedWidth(150)
        self.schedule_combo = QComboBox()
        self.schedule_combo.addItems(["Minutely", "Hourly", "Daily"])
        self.schedule_combo.currentTextChanged.connect(self._on_schedule_type_changed)
        schedule_layout.addWidget(schedule_label)
        schedule_layout.addWidget(self.schedule_combo)
        schedule_layout.addStretch()
        layout.addLayout(schedule_layout)

        # Interval value
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Every:")
        interval_label.setFixedWidth(150)
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(59)
        self.interval_spinbox.setValue(1)
        self.interval_unit_label = QLabel("minute(s)")
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spinbox)
        interval_layout.addWidget(self.interval_unit_label)
        interval_layout.addStretch()
        layout.addLayout(interval_layout)

        group.setLayout(layout)
        return group

    def _create_control_group(self):
        """Create control buttons group."""
        group = QGroupBox("Control")
        layout = QHBoxLayout()

        self.start_btn = QPushButton("Start Scheduler")
        self.start_btn.clicked.connect(self._start_scheduler)
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")

        self.stop_btn = QPushButton("Stop Scheduler")
        self.stop_btn.clicked.connect(self._stop_scheduler)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")

        test_btn = QPushButton("Send Test Request")
        test_btn.clicked.connect(self._send_test_request)

        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(test_btn)
        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_status_group(self):
        """Create status display group."""
        group = QGroupBox("Status")
        layout = QVBoxLayout()

        self.status_label = QLabel("Status: Idle")
        font = self.status_label.font()
        font.setPointSize(10)
        self.status_label.setFont(font)

        self.log_display = QLineEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setPlaceholderText("Last request status will appear here...")

        layout.addWidget(self.status_label)
        layout.addWidget(self.log_display)

        group.setLayout(layout)
        return group

    def _add_field(self):
        """Add a new field row to the table."""
        row_position = self.fields_table.rowCount()
        self.fields_table.insertRow(row_position)

        key_item = QTableWidgetItem("")
        value_item = QTableWidgetItem("")

        self.fields_table.setItem(row_position, 0, key_item)
        self.fields_table.setItem(row_position, 1, value_item)

    def _remove_field(self):
        """Remove selected field row from the table."""
        current_row = self.fields_table.currentRow()
        if current_row >= 0:
            self.fields_table.removeRow(current_row)

    def _browse_ca_certificate(self):
        """Open file dialog to select CA certificate file."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select CA Certificate File",
            "",
            "Certificate Files (*.pem *.crt *.cer);;All Files (*.*)",
        )

        if file_path:
            self.ca_cert_input.setText(file_path)

    def _on_schedule_type_changed(self):
        """Update interval spinbox based on schedule type."""
        schedule_type = self.schedule_combo.currentText()

        if schedule_type == "Minutely":
            self.interval_spinbox.setMaximum(59)
            self.interval_unit_label.setText("minute(s)")
        elif schedule_type == "Hourly":
            self.interval_spinbox.setMaximum(59)
            self.interval_unit_label.setText("hour(s)")
        elif schedule_type == "Daily":
            self.interval_spinbox.setMaximum(365)
            self.interval_unit_label.setText("day(s)")

    def _get_fields_dict(self):
        """Get fields from table as dictionary."""
        fields = {}
        for row in range(self.fields_table.rowCount()):
            key_item = self.fields_table.item(row, 0)
            value_item = self.fields_table.item(row, 1)

            if key_item and value_item and key_item.text():
                fields[key_item.text()] = value_item.text()

        return fields

    def _validate_inputs(self):
        """Validate all required inputs."""
        if not self.url_input.text():
            QMessageBox.warning(self, "Validation Error", "ServiceNow URL is required")
            return False

        if not self.username_input.text():
            QMessageBox.warning(self, "Validation Error", "Username is required")
            return False

        if not self.password_input.text():
            QMessageBox.warning(self, "Validation Error", "Password is required")
            return False

        if not self.form_input.text():
            QMessageBox.warning(self, "Validation Error", "Form/Table name is required")
            return False

        fields = self._get_fields_dict()
        if not fields:
            QMessageBox.warning(self, "Validation Error", "At least one field is required")
            return False

        return True

    def _start_scheduler(self):
        """Start the scheduler."""
        if not self._validate_inputs():
            return

        try:
            # Configure API client
            self.api_client.set_credentials(
                url=self.url_input.text(),
                username=self.username_input.text(),
                password=self.password_input.text(),
                ca_cert_path=self.ca_cert_input.text() or None,
            )

            # Configure scheduler
            schedule_type = self.schedule_combo.currentText().lower()
            interval = self.interval_spinbox.value()
            fields = self._get_fields_dict()
            form_name = self.form_input.text()

            # Create and start scheduler in separate QThread
            self.scheduler_thread = RequestSchedulerThread(
                api_client=self.api_client,
                form_name=form_name,
                fields=fields,
                schedule_type=schedule_type,
                interval=interval,
            )

            # Connect signals
            self.scheduler_thread.status_updated.connect(self._update_status_from_thread)
            self.scheduler_thread.finished.connect(self._on_scheduler_finished)

            self.scheduler_thread.start()

            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self._update_status("Scheduler started", "running")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start scheduler: {str(e)}")
            self._update_status(f"Error: {str(e)}", "error")

    def _stop_scheduler(self):
        """Stop the scheduler."""
        try:
            if self.scheduler_thread:
                self.scheduler_thread.stop_scheduler()
                self.scheduler_thread.quit()
                self.scheduler_thread.wait(timeout=5000)

            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self._update_status("Scheduler stopped", "idle")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop scheduler: {str(e)}")

    def _on_scheduler_finished(self):
        """Handle scheduler thread finished."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _update_status_from_thread(self, message, status_type):
        """Update status display from scheduler thread."""
        self._update_status(message, status_type)

    def _send_test_request(self):
        """Send a test request to ServiceNow."""
        if not self._validate_inputs():
            return

        try:
            # Configure API client
            self.api_client.set_credentials(
                url=self.url_input.text(),
                username=self.username_input.text(),
                password=self.password_input.text(),
                ca_cert_path=self.ca_cert_input.text() or None,
            )

            fields = self._get_fields_dict()
            form_name = self.form_input.text()

            # Send test request
            response = self.api_client.send_request(form_name, fields)

            if response.get("success"):
                QMessageBox.information(
                    self,
                    "Success",
                    f"Test request sent successfully!\nResponse ID: {response.get('id', 'N/A')}",
                )
                self._update_status("Test request successful", "success")
            else:
                QMessageBox.warning(
                    self,
                    "Warning",
                    f"Test request failed: {response.get('message', 'Unknown error')}",
                )
                self._update_status(f"Test request failed: {response.get('message')}", "error")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send test request: {str(e)}")
            self._update_status(f"Error: {str(e)}", "error")

    def _update_status(self, message, status_type="info"):
        """Update status display."""
        self.log_display.setText(message)

        if status_type == "running":
            self.status_label.setText("Status: Running ⏱")
            self.status_label.setStyleSheet("color: blue;")
        elif status_type == "success":
            self.status_label.setText("Status: Success ✓")
            self.status_label.setStyleSheet("color: green;")
        elif status_type == "error":
            self.status_label.setText("Status: Error ✗")
            self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setText("Status: Idle")
            self.status_label.setStyleSheet("color: black;")
