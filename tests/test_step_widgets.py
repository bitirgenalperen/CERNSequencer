"""
Unit tests for Step Widgets.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock PyQt5 if not available
try:
    from PyQt5.QtWidgets import QApplication
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

if PYQT_AVAILABLE:
    from sequencer_ui.step_widgets import (
        SetParameterWidget, WaitForEventWidget, DelayWidget,
        RunDiagnosticWidget, LogMessageWidget,
        get_step_widget_class, get_available_step_types, create_step_widget
    )


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt5 not available")
class TestStepWidgetRegistry(unittest.TestCase):
    """Test cases for step widget registry functions."""
    
    def test_get_available_step_types(self):
        """Test getting available step types."""
        step_types = get_available_step_types()
        expected_types = ["SetParameter", "WaitForEvent", "Delay", "RunDiagnostic", "LogMessage"]
        
        self.assertEqual(len(step_types), 5)
        for step_type in expected_types:
            self.assertIn(step_type, step_types)
    
    def test_get_step_widget_class(self):
        """Test getting step widget classes."""
        # Test valid step types
        self.assertEqual(get_step_widget_class("SetParameter"), SetParameterWidget)
        self.assertEqual(get_step_widget_class("WaitForEvent"), WaitForEventWidget)
        self.assertEqual(get_step_widget_class("Delay"), DelayWidget)
        self.assertEqual(get_step_widget_class("RunDiagnostic"), RunDiagnosticWidget)
        self.assertEqual(get_step_widget_class("LogMessage"), LogMessageWidget)
        
        # Test invalid step type
        self.assertIsNone(get_step_widget_class("InvalidType"))
    
    def test_create_step_widget(self):
        """Test creating step widget instances."""
        app = QApplication.instance() or QApplication([])
        
        # Test valid step types
        widget = create_step_widget("SetParameter")
        self.assertIsInstance(widget, SetParameterWidget)
        
        widget = create_step_widget("WaitForEvent")
        self.assertIsInstance(widget, WaitForEventWidget)
        
        widget = create_step_widget("Delay")
        self.assertIsInstance(widget, DelayWidget)
        
        widget = create_step_widget("RunDiagnostic")
        self.assertIsInstance(widget, RunDiagnosticWidget)
        
        widget = create_step_widget("LogMessage")
        self.assertIsInstance(widget, LogMessageWidget)
        
        # Test invalid step type
        widget = create_step_widget("InvalidType")
        self.assertIsNone(widget)


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt5 not available")
class TestSetParameterWidget(unittest.TestCase):
    """Test cases for SetParameterWidget."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication.instance() or QApplication([])
        self.widget = SetParameterWidget()
    
    def test_initialization(self):
        """Test widget initialization."""
        self.assertEqual(self.widget.get_step_type(), "SetParameter")
        self.assertEqual(self.widget.get_step_name(), "Set Parameter")
        self.assertIn("parameter", self.widget.get_step_description().lower())
    
    def test_parameters(self):
        """Test parameter get/set functionality."""
        # Test setting parameters
        params = {
            "name": "Magnet_Current_A",
            "value": 100.5,
            "units": "A"
        }
        self.widget.set_parameters(params)
        
        # Test getting parameters
        result_params = self.widget.get_parameters()
        self.assertEqual(result_params["name"], "Magnet_Current_A")
        self.assertEqual(result_params["value"], 100.5)
        self.assertEqual(result_params["units"], "A")
    
    def test_validation(self):
        """Test parameter validation."""
        # Test invalid parameters
        self.widget.set_parameters({"name": "", "value": ""})
        is_valid, errors = self.widget.validate_parameters()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Test valid parameters
        self.widget.set_parameters({"name": "Test_Param", "value": 42})
        is_valid, errors = self.widget.validate_parameters()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt5 not available")
class TestWaitForEventWidget(unittest.TestCase):
    """Test cases for WaitForEventWidget."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication.instance() or QApplication([])
        self.widget = WaitForEventWidget()
    
    def test_initialization(self):
        """Test widget initialization."""
        self.assertEqual(self.widget.get_step_type(), "WaitForEvent")
        self.assertEqual(self.widget.get_step_name(), "Wait for Event")
        self.assertIn("event", self.widget.get_step_description().lower())
    
    def test_parameters(self):
        """Test parameter get/set functionality."""
        # Test setting parameters
        params = {
            "event_name": "Beam_Ready",
            "timeout": 30.0,
            "event_source": "hardware"
        }
        self.widget.set_parameters(params)
        
        # Test getting parameters
        result_params = self.widget.get_parameters()
        self.assertEqual(result_params["event_name"], "Beam_Ready")
        self.assertEqual(result_params["timeout"], 30.0)
        self.assertEqual(result_params["event_source"], "hardware")
    
    def test_validation(self):
        """Test parameter validation."""
        # Test invalid parameters
        self.widget.set_parameters({"event_name": "", "timeout": -1})
        is_valid, errors = self.widget.validate_parameters()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Test valid parameters
        self.widget.set_parameters({"event_name": "Test_Event", "timeout": 30.0})
        is_valid, errors = self.widget.validate_parameters()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt5 not available")
class TestDelayWidget(unittest.TestCase):
    """Test cases for DelayWidget."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication.instance() or QApplication([])
        self.widget = DelayWidget()
    
    def test_initialization(self):
        """Test widget initialization."""
        self.assertEqual(self.widget.get_step_type(), "Delay")
        self.assertEqual(self.widget.get_step_name(), "Delay")
        self.assertIn("delay", self.widget.get_step_description().lower())
    
    def test_parameters(self):
        """Test parameter get/set functionality."""
        # Test setting parameters
        params = {
            "duration": 5.0,
            "precision": "high"
        }
        self.widget.set_parameters(params)
        
        # Test getting parameters
        result_params = self.widget.get_parameters()
        self.assertEqual(result_params["duration"], 5.0)
        self.assertEqual(result_params["precision"], "high")
    
    def test_validation(self):
        """Test parameter validation."""
        # Test invalid parameters
        self.widget.set_parameters({"duration": -1.0})
        is_valid, errors = self.widget.validate_parameters()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Test valid parameters
        self.widget.set_parameters({"duration": 2.5})
        is_valid, errors = self.widget.validate_parameters()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt5 not available")
class TestRunDiagnosticWidget(unittest.TestCase):
    """Test cases for RunDiagnosticWidget."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication.instance() or QApplication([])
        self.widget = RunDiagnosticWidget()
    
    def test_initialization(self):
        """Test widget initialization."""
        self.assertEqual(self.widget.get_step_type(), "RunDiagnostic")
        self.assertEqual(self.widget.get_step_name(), "Run Diagnostic")
        self.assertIn("diagnostic", self.widget.get_step_description().lower())
    
    def test_parameters(self):
        """Test parameter get/set functionality."""
        # Test setting parameters
        params = {
            "diagnostic_name": "System_Check",
            "test_parameters": {"verbose": "true"},
            "timeout": 120.0
        }
        self.widget.set_parameters(params)
        
        # Test getting parameters
        result_params = self.widget.get_parameters()
        self.assertEqual(result_params["diagnostic_name"], "System_Check")
        self.assertEqual(result_params["test_parameters"]["verbose"], "true")
        self.assertEqual(result_params["timeout"], 120.0)
    
    def test_validation(self):
        """Test parameter validation."""
        # Test invalid parameters
        self.widget.set_parameters({"diagnostic_name": "", "timeout": -1})
        is_valid, errors = self.widget.validate_parameters()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Test valid parameters
        self.widget.set_parameters({"diagnostic_name": "Test_Diagnostic", "timeout": 60.0})
        is_valid, errors = self.widget.validate_parameters()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt5 not available")
class TestLogMessageWidget(unittest.TestCase):
    """Test cases for LogMessageWidget."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication.instance() or QApplication([])
        self.widget = LogMessageWidget()
    
    def test_initialization(self):
        """Test widget initialization."""
        self.assertEqual(self.widget.get_step_type(), "LogMessage")
        self.assertEqual(self.widget.get_step_name(), "Log Message")
        self.assertIn("log", self.widget.get_step_description().lower())
    
    def test_parameters(self):
        """Test parameter get/set functionality."""
        # Test setting parameters
        params = {
            "message": "Test message",
            "log_level": "warning",
            "category": "system"
        }
        self.widget.set_parameters(params)
        
        # Test getting parameters
        result_params = self.widget.get_parameters()
        self.assertEqual(result_params["message"], "Test message")
        self.assertEqual(result_params["log_level"], "warning")
        self.assertEqual(result_params["category"], "system")
    
    def test_validation(self):
        """Test parameter validation."""
        # Test invalid parameters
        self.widget.set_parameters({"message": "", "log_level": "invalid"})
        is_valid, errors = self.widget.validate_parameters()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Test valid parameters
        self.widget.set_parameters({"message": "Valid message", "log_level": "info"})
        is_valid, errors = self.widget.validate_parameters()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt5 not available")
class TestStepWidgetIntegration(unittest.TestCase):
    """Integration tests for step widgets."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication.instance() or QApplication([])
    
    def test_all_widgets_implement_interface(self):
        """Test that all step widgets implement the required interface."""
        step_types = get_available_step_types()
        
        for step_type in step_types:
            widget = create_step_widget(step_type)
            self.assertIsNotNone(widget)
            
            # Test required methods exist
            self.assertTrue(hasattr(widget, 'get_step_type'))
            self.assertTrue(hasattr(widget, 'get_step_name'))
            self.assertTrue(hasattr(widget, 'get_step_description'))
            self.assertTrue(hasattr(widget, 'get_parameters'))
            self.assertTrue(hasattr(widget, 'set_parameters'))
            self.assertTrue(hasattr(widget, 'validate_parameters'))
            
            # Test method return types
            self.assertIsInstance(widget.get_step_type(), str)
            self.assertIsInstance(widget.get_step_name(), str)
            self.assertIsInstance(widget.get_step_description(), str)
            self.assertIsInstance(widget.get_parameters(), dict)
            
            # Test validation returns tuple
            is_valid, errors = widget.validate_parameters()
            self.assertIsInstance(is_valid, bool)
            self.assertIsInstance(errors, list)
    
    def test_widget_parameter_roundtrip(self):
        """Test that parameters can be set and retrieved correctly."""
        test_cases = [
            ("SetParameter", {"name": "Test_Param", "value": 42}),
            ("WaitForEvent", {"event_name": "Test_Event", "timeout": 30.0}),
            ("Delay", {"duration": 5.0}),
            ("RunDiagnostic", {"diagnostic_name": "Test_Diagnostic"}),
            ("LogMessage", {"message": "Test message", "log_level": "info"})
        ]
        
        for step_type, test_params in test_cases:
            widget = create_step_widget(step_type)
            
            # Set parameters
            widget.set_parameters(test_params)
            
            # Get parameters back
            result_params = widget.get_parameters()
            
            # Check that key parameters are preserved
            for key, value in test_params.items():
                self.assertIn(key, result_params)
                self.assertEqual(result_params[key], value)


if __name__ == '__main__':
    unittest.main() 