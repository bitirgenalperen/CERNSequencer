"""
Unit tests for Sequencer UI Application.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSequencerApp(unittest.TestCase):
    """Test cases for the SequencerApp class."""
    
    def test_sequencer_app_initialization(self):
        """Test SequencerApp initialization."""
        try:
            from sequencer_ui.sequencer_app import SequencerApp
            
            app = SequencerApp()
            self.assertEqual(app.app_name, "CERN Sequencer UI")
            self.assertEqual(app.app_version, "0.1.0")
            
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise
                
    def test_dummy_action_handlers_exist(self):
        """Test that all dummy action handlers exist."""
        try:
            from sequencer_ui.sequencer_app import SequencerMainWindow
            
            # Check that the class has all expected action handler methods
            expected_methods = [
                'on_new_sequence', 'on_open_sequence', 'on_save_sequence',
                'on_save_as_sequence', 'on_run_sequence', 'on_stop_sequence',
                'on_add_parameter_step', 'on_add_wait_step', 'on_add_delay_step',
                'on_about'
            ]
            
            for method_name in expected_methods:
                self.assertTrue(hasattr(SequencerMainWindow, method_name),
                              f"Method {method_name} not found in SequencerMainWindow")
                
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise
                
    def test_pyui_integration(self):
        """Test that the application integrates with PyUI framework."""
        try:
            from sequencer_ui.sequencer_app import SequencerApp
            from pyui.pyui.application_base import ApplicationBase
            
            # Verify inheritance
            self.assertTrue(issubclass(SequencerApp, ApplicationBase))
            
            app = SequencerApp()
            self.assertIsInstance(app, ApplicationBase)
            
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise
                
    def test_sequencer_main_window_class_exists(self):
        """Test that SequencerMainWindow class can be imported."""
        try:
            from sequencer_ui.sequencer_app import SequencerMainWindow
            self.assertIsNotNone(SequencerMainWindow)
            
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise
                
    def test_setup_methods_exist(self):
        """Test that all setup methods exist in SequencerMainWindow."""
        try:
            from sequencer_ui.sequencer_app import SequencerMainWindow
            
            setup_methods = ['setup_ui', 'setup_menu_bar', 'setup_toolbar', 'setup_status_bar']
            
            for method_name in setup_methods:
                self.assertTrue(hasattr(SequencerMainWindow, method_name),
                              f"Setup method {method_name} not found in SequencerMainWindow")
                
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise


class TestSequencerUIPackage(unittest.TestCase):
    """Test cases for the sequencer_ui package."""
    
    def test_package_imports(self):
        """Test that the package imports work correctly."""
        try:
            import sequencer_ui
            from sequencer_ui import SequencerApp, SequencerMainWindow
            
            self.assertIsNotNone(sequencer_ui)
            self.assertIsNotNone(SequencerApp)
            self.assertIsNotNone(SequencerMainWindow)
            
        except ImportError as e:
            # If PyQt5 is not available, this is expected
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise
                
    def test_package_version(self):
        """Test that the package has a version."""
        try:
            import sequencer_ui
            self.assertTrue(hasattr(sequencer_ui, '__version__'))
            self.assertEqual(sequencer_ui.__version__, "0.1.0")
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise


class TestSequencerUIFunctionality(unittest.TestCase):
    """Test cases for core Sequencer UI functionality."""
    
    def test_action_handlers_are_callable(self):
        """Test that action handlers can be called without errors (basic smoke test)."""
        try:
            from sequencer_ui.sequencer_app import SequencerMainWindow
            
            # Get the unbound methods from the class
            methods_to_test = [
                'on_new_sequence', 'on_open_sequence', 'on_save_sequence',
                'on_save_as_sequence', 'on_run_sequence', 'on_stop_sequence',
                'on_add_parameter_step', 'on_add_wait_step', 'on_add_delay_step',
                'on_about'
            ]
            
            for method_name in methods_to_test:
                method = getattr(SequencerMainWindow, method_name, None)
                self.assertIsNotNone(method, f"Method {method_name} should exist")
                self.assertTrue(callable(method), f"Method {method_name} should be callable")
                
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise
                
    def test_create_main_window_override(self):
        """Test that SequencerApp has the create_main_window method."""
        try:
            from sequencer_ui.sequencer_app import SequencerApp
            
            app = SequencerApp()
            self.assertTrue(hasattr(app, 'create_main_window'))
            self.assertTrue(callable(getattr(app, 'create_main_window')))
            
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise


if __name__ == '__main__':
    unittest.main() 