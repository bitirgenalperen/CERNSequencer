"""
Unit tests for the AcceleratorControlSystemInterface (Mock)

This module contains unit tests for the mock accelerator control system interface
created for Milestone 3 - Development Step 1.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sequencer_ui.accelerator_control_interface import (
    AcceleratorControlSystemInterface,
    ControlSystemStatus,
    LogLevel,
    set_parameter,
    wait_for_event,
    delay,
    run_diagnostic,
    log_message
)


class TestAcceleratorControlSystemInterface(unittest.TestCase):
    """Test cases for the AcceleratorControlSystemInterface class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.interface = AcceleratorControlSystemInterface()
    
    def test_interface_initialization(self):
        """Test that the interface initializes correctly."""
        self.assertTrue(self.interface.connected)
        self.assertTrue(self.interface.simulation_mode)
        self.assertIsInstance(self.interface.parameter_store, dict)
        self.assertIsInstance(self.interface.event_registry, dict)
        self.assertIsInstance(self.interface.diagnostic_results, dict)
        self.assertIsInstance(self.interface.log_buffer, list)
        
        # Check that default parameters are initialized
        self.assertIn("Magnet_Current_A", self.interface.parameter_store)
        self.assertIn("RF_Frequency_B", self.interface.parameter_store)
        self.assertIn("Beam_Ready_Signal", self.interface.event_registry)
        self.assertIn("Vacuum_Ready", self.interface.event_registry)
    
    def test_set_parameter_success(self):
        """Test successful parameter setting."""
        result = self.interface.set_parameter("Test_Parameter", 42.5, "V")
        
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        self.assertEqual(result["parameter"], "Test_Parameter")
        self.assertEqual(result["value"], 42.5)
        self.assertEqual(result["units"], "V")
        self.assertIn("execution_time", result)
        self.assertIn("Test_Parameter", self.interface.parameter_store)
        self.assertEqual(self.interface.parameter_store["Test_Parameter"], 42.5)
    
    def test_set_parameter_type_conversion(self):
        """Test parameter type conversion."""
        # Test string to float conversion
        result = self.interface.set_parameter("Float_Param", "123.45")
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        self.assertEqual(self.interface.parameter_store["Float_Param"], 123.45)
        
        # Test string to int conversion
        result = self.interface.set_parameter("Int_Param", "123")
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        self.assertEqual(self.interface.parameter_store["Int_Param"], 123)
        
        # Test string that can't be converted
        result = self.interface.set_parameter("String_Param", "not_a_number")
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        self.assertEqual(self.interface.parameter_store["String_Param"], "not_a_number")
    
    def test_set_parameter_validation_warning(self):
        """Test parameter validation warning for magnet parameters."""
        # Test value outside normal range
        result = self.interface.set_parameter("Magnet_Current_X", 2000, "A")
        self.assertEqual(result["status"], ControlSystemStatus.WARNING.value)
        self.assertIn("outside normal range", result["message"])
        self.assertEqual(result["parameter"], "Magnet_Current_X")
        self.assertEqual(result["value"], 2000)
    
    def test_get_parameter(self):
        """Test parameter retrieval."""
        # Set a parameter first
        self.interface.set_parameter("Test_Get", 99.9)
        
        # Get the parameter
        result = self.interface.get_parameter("Test_Get")
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        self.assertEqual(result["parameter"], "Test_Get")
        self.assertEqual(result["value"], 99.9)
        
        # Test non-existent parameter
        result = self.interface.get_parameter("Non_Existent")
        self.assertEqual(result["status"], ControlSystemStatus.FAILURE.value)
        self.assertIn("not found", result["message"])
    
    def test_wait_for_event_success(self):
        """Test successful event waiting."""
        # This test depends on random event occurrence, so we'll use a short timeout
        # and accept either success or timeout
        result = self.interface.wait_for_event("Beam_Ready_Signal", 0.1)
        self.assertIn(result["status"], [ControlSystemStatus.SUCCESS.value, ControlSystemStatus.TIMEOUT.value])
        self.assertEqual(result["event_name"], "Beam_Ready_Signal")
        self.assertIn("execution_time", result)
    
    def test_wait_for_event_timeout(self):
        """Test event waiting timeout."""
        # Use a very short timeout to ensure timeout occurs
        result = self.interface.wait_for_event("Test_Event_Never_Occurs", 0.01)
        self.assertEqual(result["status"], ControlSystemStatus.TIMEOUT.value)
        self.assertIn("Timeout", result["message"])
    
    def test_delay_normal_precision(self):
        """Test delay with normal precision."""
        start_time = time.time()
        result = self.interface.delay(0.1, "normal", True)
        end_time = time.time()
        
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        self.assertEqual(result["requested_duration"], 0.1)
        self.assertAlmostEqual(result["actual_duration"], end_time - start_time, delta=0.05)
        self.assertEqual(result["precision"], "normal")
    
    def test_delay_different_precisions(self):
        """Test delay with different precision settings."""
        for precision in ["high", "low", "normal"]:
            result = self.interface.delay(0.05, precision, True)
            self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
            self.assertEqual(result["precision"], precision)
    
    def test_run_diagnostic_success(self):
        """Test diagnostic execution with parameters."""
        test_params = {"verbose": "true", "timeout": "30"}
        result = self.interface.run_diagnostic("Test_Diagnostic", test_params, "system")
        
        # Accept either success or failure since it's random
        self.assertIn(result["status"], [ControlSystemStatus.SUCCESS.value, ControlSystemStatus.FAILURE.value])
        self.assertIn("diagnostic_results", result)
        self.assertEqual(result["diagnostic_results"]["diagnostic_name"], "Test_Diagnostic")
        self.assertEqual(result["diagnostic_results"]["test_category"], "system")
        self.assertEqual(result["diagnostic_results"]["test_parameters"], test_params)
        self.assertIn("Test_Diagnostic", self.interface.diagnostic_results)
    
    def test_run_diagnostic_without_parameters(self):
        """Test diagnostic execution without parameters."""
        result = self.interface.run_diagnostic("Simple_Diagnostic")
        
        # Accept either success or failure since it's random
        self.assertIn(result["status"], [ControlSystemStatus.SUCCESS.value, ControlSystemStatus.FAILURE.value])
        self.assertIn("diagnostic_results", result)
        self.assertEqual(result["diagnostic_results"]["test_parameters"], {})
    
    def test_log_message_different_levels(self):
        """Test logging messages with different severity levels."""
        test_cases = [
            ("Debug message", "debug"),
            ("Info message", "info"),
            ("Warning message", "warning"),
            ("Error message", "error"),
            ("Critical message", "critical")
        ]
        
        for message, level in test_cases:
            result = self.interface.log_message(message, level, "test")
            self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
            self.assertEqual(result["log_entry"]["message"], message)
            self.assertEqual(result["log_entry"]["log_level"], level)
            self.assertEqual(result["log_entry"]["category"], "test")
    
    def test_log_message_invalid_level(self):
        """Test logging with invalid log level."""
        result = self.interface.log_message("Test message", "invalid_level")
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        # Should default to "info" level
        self.assertEqual(result["log_entry"]["log_level"], "info")
    
    def test_log_message_formatting(self):
        """Test log message formatting options."""
        result = self.interface.log_message(
            "Test message", 
            "info", 
            "test_category",
            include_timestamp=True,
            include_step_info=True
        )
        
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        formatted_msg = result["log_entry"]["formatted_message"]
        self.assertIn("TEST_CATEGORY", formatted_msg)
        self.assertIn("Test message", formatted_msg)
    
    def test_get_event_status(self):
        """Test event status retrieval."""
        # Test existing event
        result = self.interface.get_event_status("Beam_Ready_Signal")
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        self.assertEqual(result["event_name"], "Beam_Ready_Signal")
        self.assertIn("event_status", result)
        
        # Test non-existent event
        result = self.interface.get_event_status("Non_Existent_Event")
        self.assertEqual(result["status"], ControlSystemStatus.FAILURE.value)
        self.assertIn("not found", result["message"])
    
    def test_get_system_status(self):
        """Test system status retrieval."""
        result = self.interface.get_system_status()
        
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        self.assertEqual(result["connected"], True)
        self.assertEqual(result["simulation_mode"], True)
        self.assertIn("parameters_count", result)
        self.assertIn("events_count", result)
        self.assertIn("diagnostics_count", result)
        self.assertIn("log_entries_count", result)
    
    def test_reset_system(self):
        """Test system reset functionality."""
        # Add some data first
        self.interface.set_parameter("Test_Reset", 123)
        self.interface.log_message("Test log", "info")
        
        # Reset the system
        result = self.interface.reset_system()
        
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        self.assertIn("reset completed", result["message"])
        
        # Check that data was cleared and defaults restored
        self.assertIn("Magnet_Current_A", self.interface.parameter_store)  # Default should be restored
        self.assertNotIn("Test_Reset", self.interface.parameter_store)  # Custom should be cleared
    
    def test_log_buffer_limit(self):
        """Test that log buffer maintains size limit."""
        # Add many log entries
        for i in range(1010):  # More than the 1000 limit
            self.interface.log_message(f"Test message {i}", "info")
        
        # Check that buffer is limited to 1000 entries
        self.assertEqual(len(self.interface.log_buffer), 1000)
        
        # Check that the oldest entries were removed
        first_entry = self.interface.log_buffer[0]
        self.assertIn("Test message 1", first_entry["message"])  # Should start from message 10+


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for the convenience functions."""
    
    def test_set_parameter_function(self):
        """Test the set_parameter convenience function."""
        result = set_parameter("Test_Convenience", 42.0, units="V")
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        self.assertEqual(result["parameter"], "Test_Convenience")
        self.assertEqual(result["value"], 42.0)
    
    def test_wait_for_event_function(self):
        """Test the wait_for_event convenience function."""
        result = wait_for_event("Test_Event", 0.01)
        self.assertIn(result["status"], [ControlSystemStatus.SUCCESS.value, ControlSystemStatus.TIMEOUT.value])
        self.assertEqual(result["event_name"], "Test_Event")
    
    def test_delay_function(self):
        """Test the delay convenience function."""
        result = delay(0.01, precision="normal")
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        self.assertEqual(result["requested_duration"], 0.01)
    
    def test_run_diagnostic_function(self):
        """Test the run_diagnostic convenience function."""
        result = run_diagnostic("Test_Diag", {"param": "value"})
        # Accept either success or failure since it's random
        self.assertIn(result["status"], [ControlSystemStatus.SUCCESS.value, ControlSystemStatus.FAILURE.value])
        self.assertIn("diagnostic_results", result)
    
    def test_log_message_function(self):
        """Test the log_message convenience function."""
        result = log_message("Test convenience log", "info")
        self.assertEqual(result["status"], ControlSystemStatus.SUCCESS.value)
        self.assertEqual(result["log_entry"]["message"], "Test convenience log")


if __name__ == '__main__':
    unittest.main() 