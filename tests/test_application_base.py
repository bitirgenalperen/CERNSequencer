"""
Unit tests for PyUI ApplicationBase class.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import pyui
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyui.pyui.application_base import ApplicationBase


class TestApplicationBase(unittest.TestCase):
    """Test cases for the ApplicationBase class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app_base = ApplicationBase("Test App", "1.0.0")
        
    def test_initialization(self):
        """Test ApplicationBase initialization."""
        self.assertEqual(self.app_base.app_name, "Test App")
        self.assertEqual(self.app_base.app_version, "1.0.0")
        self.assertIsNone(self.app_base.app)
        self.assertIsNone(self.app_base.main_window)
        
    def test_default_initialization(self):
        """Test ApplicationBase initialization with default values."""
        default_app = ApplicationBase()
        self.assertEqual(default_app.app_name, "PyUI Application")
        self.assertEqual(default_app.app_version, "1.0.0")
        
    @patch('pyui.pyui.application_base.QApplication')
    def test_initialize_application(self, mock_qapp):
        """Test application initialization."""
        # Mock QApplication.instance() to return None (no existing instance)
        mock_qapp.instance.return_value = None
        mock_app_instance = MagicMock()
        mock_qapp.return_value = mock_app_instance
        
        result = self.app_base.initialize_application()
        
        # Verify QApplication was created
        mock_qapp.assert_called_once()
        self.assertEqual(result, mock_app_instance)
        self.assertEqual(self.app_base.app, mock_app_instance)
        
        # Verify application properties were set
        mock_app_instance.setApplicationName.assert_called_with("Test App")
        mock_app_instance.setApplicationVersion.assert_called_with("1.0.0")
        mock_app_instance.setOrganizationName.assert_called_with("CERN")
        
    @patch('pyui.pyui.application_base.QApplication')
    def test_initialize_application_existing_instance(self, mock_qapp):
        """Test application initialization when QApplication instance already exists."""
        existing_instance = MagicMock()
        mock_qapp.instance.return_value = existing_instance
        
        result = self.app_base.initialize_application()
        
        # Verify existing instance was used
        self.assertEqual(result, existing_instance)
        self.assertEqual(self.app_base.app, existing_instance)
        
    @patch('pyui.pyui.application_base.QMainWindow')
    def test_create_main_window_default(self, mock_main_window):
        """Test main window creation with default QMainWindow."""
        mock_window_instance = MagicMock()
        mock_main_window.return_value = mock_window_instance
        
        result = self.app_base.create_main_window()
        
        mock_main_window.assert_called_once()
        self.assertEqual(result, mock_window_instance)
        self.assertEqual(self.app_base.main_window, mock_window_instance)
        
        # Verify window properties were set
        mock_window_instance.setWindowTitle.assert_called_with("Test App")
        mock_window_instance.setMinimumSize.assert_called_with(800, 600)
        
    @patch('pyui.pyui.application_base.QMainWindow')
    def test_create_main_window_custom(self, mock_main_window):
        """Test main window creation with custom window class."""
        custom_window_class = MagicMock()
        custom_window_instance = MagicMock()
        custom_window_class.return_value = custom_window_instance
        
        result = self.app_base.create_main_window(custom_window_class)
        
        custom_window_class.assert_called_once()
        self.assertEqual(result, custom_window_instance)
        self.assertEqual(self.app_base.main_window, custom_window_instance)
        
    def test_setup_ui_default(self):
        """Test that setup_ui method exists and can be called."""
        # The default implementation should do nothing
        try:
            self.app_base.setup_ui()
        except Exception as e:
            self.fail(f"setup_ui() raised an exception: {e}")
            
    @patch.object(ApplicationBase, 'setup_ui')
    @patch.object(ApplicationBase, 'create_main_window')
    @patch.object(ApplicationBase, 'initialize_application')
    def test_run_method(self, mock_init_app, mock_create_window, mock_setup_ui):
        """Test the run method workflow."""
        # Mock the application and window
        mock_app = MagicMock()
        mock_window = MagicMock()
        mock_init_app.return_value = mock_app
        mock_create_window.return_value = mock_window
        mock_app.exec_.return_value = 0
        
        # Ensure the app is set when initialize_application is called
        def set_app(*args, **kwargs):
            self.app_base.app = mock_app
            return mock_app
        mock_init_app.side_effect = set_app
        
        # Ensure the main_window is set when create_main_window is called
        def set_main_window(*args, **kwargs):
            self.app_base.main_window = mock_window
            return mock_window
        mock_create_window.side_effect = set_main_window
        
        result = self.app_base.run()
        
        # Verify the workflow
        mock_init_app.assert_called_once()
        mock_create_window.assert_called_once()
        mock_setup_ui.assert_called_once()
        mock_window.show.assert_called_once()
        mock_app.exec_.assert_called_once()
        
        self.assertEqual(result, 0)
        
    def test_quit_method(self):
        """Test the quit method."""
        # Test with no app
        self.app_base.quit()  # Should not raise exception
        
        # Test with app
        mock_app = MagicMock()
        self.app_base.app = mock_app
        self.app_base.quit()
        mock_app.quit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
