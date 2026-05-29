#!/usr/bin/env python3
"""
ServiceNow Data Access Request Application
A PyQt5-based GUI application for sending scheduled API requests to ServiceNow forms.
"""

import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
