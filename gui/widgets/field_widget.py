"""
Widget for managing custom fields in the ServiceNow request.
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt5.QtCore import pyqtSignal


class FieldWidget(QWidget):
    """A widget representing a single key-value field pair."""

    removed = pyqtSignal()

    def __init__(self, key="", value="", parent=None):
        super().__init__(parent)
        self.init_ui(key, value)

    def init_ui(self, key, value):
        """Initialize the UI."""
        layout = QHBoxLayout()

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Field name")
        self.key_input.setText(key)

        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Field value")
        self.value_input.setText(value)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.removed.emit)
        remove_btn.setMaximumWidth(80)

        layout.addWidget(self.key_input)
        layout.addWidget(self.value_input)
        layout.addWidget(remove_btn)

        self.setLayout(layout)

    def get_key(self):
        """Get the field key."""
        return self.key_input.text()

    def get_value(self):
        """Get the field value."""
        return self.value_input.text()

    def set_key(self, key):
        """Set the field key."""
        self.key_input.setText(key)

    def set_value(self, value):
        """Set the field value."""
        self.value_input.setText(value)
