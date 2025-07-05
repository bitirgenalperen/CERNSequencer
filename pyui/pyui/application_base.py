"""
PyUI Application Base

Provides the foundational application class for PyUI-based applications.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class ApplicationBase:
    """Base class for PyUI applications providing common PyQt setup."""
    
    def __init__(self, app_name="PyUI Application", app_version="1.0.0"):
        """Initialize the PyUI application base.
        
        Args:
            app_name (str): Name of the application
            app_version (str): Version of the application
        """
        self.app_name = app_name
        self.app_version = app_version
        self.app = None
        self.main_window = None
        
    def initialize_application(self):
        """Initialize the PyQt application instance."""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
            
        # Set application properties
        self.app.setApplicationName(self.app_name)
        self.app.setApplicationVersion(self.app_version)
        self.app.setOrganizationName("CERN")
        
        # Set default style and behavior
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        
        return self.app
    
    def create_main_window(self, window_class=None):
        """Create the main application window.
        
        Args:
            window_class: Custom QMainWindow subclass. If None, uses QMainWindow.
            
        Returns:
            QMainWindow: The created main window
        """
        if window_class is None:
            window_class = QMainWindow
            
        self.main_window = window_class()
        self.main_window.setWindowTitle(self.app_name)
        
        # Set minimum size for better UX
        self.main_window.setMinimumSize(800, 600)
        
        return self.main_window
    
    def setup_ui(self):
        """Override this method to set up the UI components.
        
        This method should be implemented by subclasses to define
        their specific UI layout and components.
        """
        pass
    
    def run(self):
        """Start the application event loop.
        
        Returns:
            int: Application exit code
        """
        if not self.app:
            self.initialize_application()
            
        if not self.main_window:
            self.create_main_window()
            
        # Set up the UI
        self.setup_ui()
        
        # Show the main window
        self.main_window.show()
        
        # Start the event loop
        return self.app.exec_()
    
    def quit(self):
        """Quit the application gracefully."""
        if self.app:
            self.app.quit()
