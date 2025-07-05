"""
Unit tests for Hello World Example.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestHelloWorldExample(unittest.TestCase):
    """Test cases for the Hello World example."""
    
    def test_hello_world_import(self):
        """Test that Hello World example can be imported."""
        try:
            from pyui.hello_world_example import HelloWorldApp, HelloWorldWindow
            self.assertIsNotNone(HelloWorldApp)
            self.assertIsNotNone(HelloWorldWindow)
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise
                
    def test_hello_world_app_inheritance(self):
        """Test that HelloWorldApp inherits from ApplicationBase."""
        try:
            from pyui.hello_world_example import HelloWorldApp
            from pyui.pyui.application_base import ApplicationBase
            
            self.assertTrue(issubclass(HelloWorldApp, ApplicationBase))
            
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise
                
    def test_hello_world_app_initialization(self):
        """Test HelloWorldApp initialization."""
        try:
            from pyui.hello_world_example import HelloWorldApp
            
            app = HelloWorldApp()
            self.assertEqual(app.app_name, "PyUI Hello World")
            self.assertEqual(app.app_version, "1.0.0")
            
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyUI Hello World")
            else:
                raise
                
    def test_hello_world_window_methods(self):
        """Test that HelloWorldWindow has expected methods."""
        try:
            from pyui.hello_world_example import HelloWorldWindow
            
            expected_methods = ['setup_ui', 'on_hello_clicked', 'on_clear_clicked']
            
            for method_name in expected_methods:
                self.assertTrue(hasattr(HelloWorldWindow, method_name),
                              f"Method {method_name} not found in HelloWorldWindow")
                
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise
                
    def test_hello_world_main_function(self):
        """Test that main function exists and is callable."""
        try:
            from pyui.hello_world_example import main
            
            self.assertTrue(callable(main))
            
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise


if __name__ == '__main__':
    unittest.main() 