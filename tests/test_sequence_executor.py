"""
Unit tests for the SequenceExecutor Module

This module contains unit tests for the sequence executor component
created for Milestone 3 - Development Step 2: Sequence Executor Logic.
"""

import unittest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QSignalSpy

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sequencer_ui.sequence_executor import (
    SequenceExecutor,
    ExecutionState,
    ExecutionMode,
    SequenceExecutionThread,
    create_default_executor
)
from sequencer_ui.sequence_data_model import (
    SequenceData,
    SequenceStep,
    StepType,
    StepStatus,
    create_set_parameter_step,
    create_wait_for_event_step,
    create_delay_step,
    create_run_diagnostic_step,
    create_log_message_step
)
from sequencer_ui.accelerator_control_interface import (
    AcceleratorControlSystemInterface,
    ControlSystemStatus
)


class TestSequenceExecutor(unittest.TestCase):
    """Test cases for the SequenceExecutor class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock control interface
        self.mock_interface = Mock(spec=AcceleratorControlSystemInterface)
        self.mock_interface.set_parameter.return_value = {
            "status": ControlSystemStatus.SUCCESS.value,
            "message": "Parameter set successfully",
            "execution_time": 0.1
        }
        self.mock_interface.wait_for_event.return_value = {
            "status": ControlSystemStatus.SUCCESS.value,
            "message": "Event occurred",
            "execution_time": 0.5
        }
        self.mock_interface.delay.return_value = {
            "status": ControlSystemStatus.SUCCESS.value,
            "message": "Delay completed",
            "execution_time": 1.0
        }
        self.mock_interface.run_diagnostic.return_value = {
            "status": ControlSystemStatus.SUCCESS.value,
            "message": "Diagnostic completed",
            "execution_time": 2.0
        }
        self.mock_interface.log_message.return_value = {
            "status": ControlSystemStatus.SUCCESS.value,
            "message": "Message logged",
            "execution_time": 0.01
        }
        
        # Create executor with mock interface
        self.executor = SequenceExecutor(self.mock_interface)
        
        # Create test sequence
        self.test_sequence = self._create_test_sequence()
    
    def tearDown(self):
        """Clean up after each test."""
        # Stop any running execution
        if self.executor.state in [ExecutionState.RUNNING, ExecutionState.PAUSED]:
            self.executor.stop_execution()
            # Wait a bit for cleanup
            self.app.processEvents()
            time.sleep(0.1)
    
    def _create_test_sequence(self) -> SequenceData:
        """Create a test sequence with various step types."""
        sequence = SequenceData()
        sequence.metadata.name = "Test Sequence"
        sequence.metadata.description = "A test sequence for unit testing"
        
        # Add different types of steps
        steps = [
            create_log_message_step("Starting test sequence", "info"),
            create_set_parameter_step("Test_Parameter", 42.0),
            create_delay_step(0.1),
            create_run_diagnostic_step("Test_Diagnostic", {"param": "value"}),
            create_wait_for_event_step("Test_Event", 1.0),
            create_log_message_step("Test sequence completed", "info")
        ]
        
        for step in steps:
            sequence.add_step(step)
        
        return sequence
    
    def test_executor_initialization(self):
        """Test that the executor initializes correctly."""
        # Test with provided interface
        executor = SequenceExecutor(self.mock_interface)
        self.assertEqual(executor.control_interface, self.mock_interface)
        self.assertEqual(executor.state, ExecutionState.IDLE)
        self.assertEqual(executor.mode, ExecutionMode.NORMAL)
        self.assertIsNone(executor.current_sequence)
        self.assertEqual(executor.current_step_index, 0)
        self.assertFalse(executor.stop_requested)
        self.assertFalse(executor.pause_requested)
        
        # Test default interface creation
        executor_default = SequenceExecutor()
        self.assertIsInstance(executor_default.control_interface, AcceleratorControlSystemInterface)
    
    def test_execution_state_enum(self):
        """Test the ExecutionState enum."""
        self.assertEqual(ExecutionState.IDLE.value, "idle")
        self.assertEqual(ExecutionState.RUNNING.value, "running")
        self.assertEqual(ExecutionState.PAUSED.value, "paused")
        self.assertEqual(ExecutionState.COMPLETED.value, "completed")
        self.assertEqual(ExecutionState.FAILED.value, "failed")
    
    def test_execution_mode_enum(self):
        """Test the ExecutionMode enum."""
        self.assertEqual(ExecutionMode.NORMAL.value, "normal")
        self.assertEqual(ExecutionMode.STEP_BY_STEP.value, "step_by_step")
        self.assertEqual(ExecutionMode.DRY_RUN.value, "dry_run")
    
    def test_dry_run_execution(self):
        """Test dry run execution mode."""
        # Test successful dry run
        result = self.executor.execute_sequence(self.test_sequence, ExecutionMode.DRY_RUN)
        self.assertTrue(result)
        
        # Verify no actual interface calls were made
        self.mock_interface.set_parameter.assert_not_called()
        self.mock_interface.wait_for_event.assert_not_called()
        self.mock_interface.delay.assert_not_called()
        self.mock_interface.run_diagnostic.assert_not_called()
        self.mock_interface.log_message.assert_not_called()
    
    def test_dry_run_with_invalid_sequence(self):
        """Test dry run with invalid sequence."""
        # Create invalid sequence
        invalid_sequence = SequenceData()
        invalid_step = SequenceStep(
            step_type=StepType.SET_PARAMETER,
            parameters={}  # Missing required parameters
        )
        invalid_sequence.add_step(invalid_step)
        
        result = self.executor.execute_sequence(invalid_sequence, ExecutionMode.DRY_RUN)
        self.assertFalse(result)
    
    def test_step_validation(self):
        """Test step validation methods."""
        # Test valid SetParameter step
        step = create_set_parameter_step("Test_Param", 123)
        is_valid, errors = self.executor._validate_step(step)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Test invalid SetParameter step
        invalid_step = SequenceStep(
            step_type=StepType.SET_PARAMETER,
            parameters={"name": "", "value": 123}  # Empty name
        )
        is_valid, errors = self.executor._validate_step(invalid_step)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_step_validators(self):
        """Test individual step validators."""
        # Test SetParameter validator
        step = create_set_parameter_step("Test", 123)
        is_valid, errors = self.executor._validate_set_parameter_step(step)
        self.assertTrue(is_valid)
        
        # Test WaitForEvent validator
        step = create_wait_for_event_step("Test_Event", 30.0)
        is_valid, errors = self.executor._validate_wait_for_event_step(step)
        self.assertTrue(is_valid)
        
        # Test Delay validator
        step = create_delay_step(1.0)
        is_valid, errors = self.executor._validate_delay_step(step)
        self.assertTrue(is_valid)
        
        # Test RunDiagnostic validator
        step = create_run_diagnostic_step("Test_Diag")
        is_valid, errors = self.executor._validate_run_diagnostic_step(step)
        self.assertTrue(is_valid)
        
        # Test LogMessage validator
        step = create_log_message_step("Test message")
        is_valid, errors = self.executor._validate_log_message_step(step)
        self.assertTrue(is_valid)
    
    def test_step_execution_methods(self):
        """Test individual step execution methods."""
        # Test SetParameter execution
        step = create_set_parameter_step("Test_Param", 42.0)
        step.parameters["units"] = "V"  # Add units after creation
        result = self.executor._execute_set_parameter_step(step)
        self.mock_interface.set_parameter.assert_called_once_with(
            name="Test_Param", value=42.0, units="V", timeout=None
        )
        
        # Test WaitForEvent execution
        step = create_wait_for_event_step("Test_Event", 30.0)
        result = self.executor._execute_wait_for_event_step(step)
        self.mock_interface.wait_for_event.assert_called_once()
        
        # Test Delay execution
        step = create_delay_step(1.0)
        result = self.executor._execute_delay_step(step)
        self.mock_interface.delay.assert_called_once_with(
            duration=1.0, precision="normal", interruptible=True
        )
        
        # Test RunDiagnostic execution
        step = create_run_diagnostic_step("Test_Diag", {"param": "value"})
        result = self.executor._execute_run_diagnostic_step(step)
        self.mock_interface.run_diagnostic.assert_called_once()
        
        # Test LogMessage execution
        step = create_log_message_step("Test message", "info")
        result = self.executor._execute_log_message_step(step)
        self.mock_interface.log_message.assert_called_once()
    
    def test_execution_control(self):
        """Test execution control methods."""
        # Test pause
        self.executor.state = ExecutionState.RUNNING
        self.executor.pause_execution()
        self.assertTrue(self.executor.pause_requested)
        
        # Test resume
        self.executor.state = ExecutionState.PAUSED
        self.executor.resume_execution()
        self.assertFalse(self.executor.pause_requested)
        
        # Test stop
        self.executor.state = ExecutionState.RUNNING
        self.executor.stop_execution()
        self.assertTrue(self.executor.stop_requested)
    
    def test_execution_status(self):
        """Test execution status reporting."""
        status = self.executor.get_execution_status()
        
        # Check required fields
        self.assertIn("state", status)
        self.assertIn("mode", status)
        self.assertIn("sequence_id", status)
        self.assertIn("current_step_index", status)
        self.assertIn("total_steps_executed", status)
        self.assertIn("successful_steps", status)
        self.assertIn("failed_steps", status)
        
        # Test with active sequence
        self.executor.current_sequence = self.test_sequence
        status = self.executor.get_execution_status()
        self.assertEqual(status["sequence_id"], self.test_sequence.sequence_id)
        self.assertEqual(status["sequence_name"], self.test_sequence.metadata.name)
    
    def test_state_reset(self):
        """Test execution state reset."""
        # Set some state
        self.executor.current_sequence = self.test_sequence
        self.executor.current_step_index = 5
        self.executor.successful_steps = 3
        self.executor.failed_steps = 1
        
        # Reset state
        self.executor._reset_execution_state()
        
        # Verify reset
        self.assertEqual(self.executor.state, ExecutionState.IDLE)
        self.assertIsNone(self.executor.current_sequence)
        self.assertEqual(self.executor.current_step_index, 0)
        self.assertEqual(self.executor.successful_steps, 0)
        self.assertEqual(self.executor.failed_steps, 0)
        self.assertFalse(self.executor.stop_requested)
        self.assertFalse(self.executor.pause_requested)
    
    def test_invalid_execution_start(self):
        """Test starting execution when executor is not idle."""
        # Set executor to running state
        self.executor.state = ExecutionState.RUNNING
        
        # Try to start execution
        result = self.executor.execute_sequence(self.test_sequence)
        self.assertFalse(result)
    
    def test_invalid_sequence_execution(self):
        """Test execution with invalid sequence."""
        # Create sequence with empty name (invalid)
        invalid_sequence = SequenceData()
        invalid_sequence.metadata.name = ""  # Invalid empty name
        
        result = self.executor.execute_sequence(invalid_sequence)
        self.assertFalse(result)
    
    def test_step_execution_with_errors(self):
        """Test step execution with various error conditions."""
        # Mock interface to return failure
        self.mock_interface.set_parameter.return_value = {
            "status": ControlSystemStatus.FAILURE.value,
            "message": "Parameter setting failed"
        }
        
        step = create_set_parameter_step("Test_Param", 42.0)
        
        # Set up executor with a test sequence for step execution
        self.executor.current_sequence = self.test_sequence
        success = self.executor._execute_step(step, 1, 1)
        
        self.assertFalse(success)
        self.assertEqual(step.status, StepStatus.FAILED)
        self.assertIsNotNone(step.error_message)
    
    def test_step_execution_with_warnings(self):
        """Test step execution with warning status."""
        # Mock interface to return warning
        self.mock_interface.set_parameter.return_value = {
            "status": ControlSystemStatus.WARNING.value,
            "message": "Parameter set with warning"
        }
        
        step = create_set_parameter_step("Test_Param", 42.0)
        
        # Set up executor with a test sequence for step execution
        self.executor.current_sequence = self.test_sequence
        success = self.executor._execute_step(step, 1, 1)
        
        self.assertTrue(success)  # Warnings are treated as success
        self.assertEqual(step.status, StepStatus.COMPLETED)
    
    def test_step_execution_with_exception(self):
        """Test step execution when interface raises exception."""
        # Mock interface to raise exception
        self.mock_interface.set_parameter.side_effect = Exception("Test exception")
        
        step = create_set_parameter_step("Test_Param", 42.0)
        
        # Set up executor with a test sequence for step execution
        self.executor.current_sequence = self.test_sequence
        success = self.executor._execute_step(step, 1, 1)
        
        self.assertFalse(success)
        self.assertEqual(step.status, StepStatus.FAILED)
        self.assertIn("Exception executing step", step.error_message)
    
    def test_unknown_step_type_execution(self):
        """Test execution of unknown step type."""
        # Create step with unknown type (we'll modify it directly)
        step = create_set_parameter_step("Test", 123)
        step.step_type = "UnknownType"  # Invalid step type
        
        result = self.executor._execute_step_by_type(step)
        self.assertEqual(result["status"], ControlSystemStatus.FAILURE.value)
        self.assertIn("Unknown step type", result["message"])


class TestSequenceExecutionThread(unittest.TestCase):
    """Test cases for the SequenceExecutionThread class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_interface = Mock(spec=AcceleratorControlSystemInterface)
        self.executor = SequenceExecutor(self.mock_interface)
    
    def test_thread_creation(self):
        """Test thread creation and initialization."""
        thread = SequenceExecutionThread(self.executor)
        self.assertEqual(thread.executor, self.executor)
        self.assertIsInstance(thread, SequenceExecutionThread)
    
    def test_thread_run_method_exists(self):
        """Test that the thread has a run method."""
        thread = SequenceExecutionThread(self.executor)
        self.assertTrue(hasattr(thread, 'run'))
        self.assertTrue(callable(getattr(thread, 'run')))


class TestExecutorSignals(unittest.TestCase):
    """Test cases for executor signals."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_interface = Mock(spec=AcceleratorControlSystemInterface)
        self.executor = SequenceExecutor(self.mock_interface)
    
    def test_executor_has_required_signals(self):
        """Test that executor has all required signals."""
        required_signals = [
            'execution_started',
            'execution_completed',
            'execution_paused',
            'execution_resumed',
            'execution_stopped',
            'execution_failed',
            'step_started',
            'step_completed',
            'step_failed',
            'step_skipped',
            'progress_updated',
            'status_message'
        ]
        
        for signal_name in required_signals:
            self.assertTrue(hasattr(self.executor, signal_name))
            signal_obj = getattr(self.executor, signal_name)
            # Check that it's a pyqtSignal
            self.assertTrue(hasattr(signal_obj, 'emit'))


class TestExecutorValidation(unittest.TestCase):
    """Test cases for step validation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = SequenceExecutor()
    
    def test_set_parameter_validation(self):
        """Test SetParameter step validation."""
        # Valid step
        step = create_set_parameter_step("Valid_Param", 123)
        is_valid, errors = self.executor._validate_set_parameter_step(step)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid step - empty name
        step.parameters["name"] = ""
        is_valid, errors = self.executor._validate_set_parameter_step(step)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Invalid step - missing value
        step.parameters = {"name": "Valid_Name"}
        is_valid, errors = self.executor._validate_set_parameter_step(step)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_wait_for_event_validation(self):
        """Test WaitForEvent step validation."""
        # Valid step
        step = create_wait_for_event_step("Valid_Event", 30.0)
        is_valid, errors = self.executor._validate_wait_for_event_step(step)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid step - empty event name
        step.parameters["event_name"] = ""
        is_valid, errors = self.executor._validate_wait_for_event_step(step)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Invalid step - negative timeout
        step.parameters["event_name"] = "Valid_Event"
        step.parameters["timeout"] = -1.0
        is_valid, errors = self.executor._validate_wait_for_event_step(step)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_delay_validation(self):
        """Test Delay step validation."""
        # Valid step
        step = create_delay_step(1.0)
        is_valid, errors = self.executor._validate_delay_step(step)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid step - negative duration
        step.parameters["duration"] = -1.0
        is_valid, errors = self.executor._validate_delay_step(step)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Invalid step - invalid precision
        step.parameters["duration"] = 1.0
        step.parameters["precision"] = "invalid"
        is_valid, errors = self.executor._validate_delay_step(step)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_log_message_validation(self):
        """Test LogMessage step validation."""
        # Valid step
        step = create_log_message_step("Valid message", "info")
        is_valid, errors = self.executor._validate_log_message_step(step)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid step - empty message
        step.parameters["message"] = ""
        is_valid, errors = self.executor._validate_log_message_step(step)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Invalid step - invalid log level
        step.parameters["message"] = "Valid message"
        step.parameters["log_level"] = "invalid_level"
        is_valid, errors = self.executor._validate_log_message_step(step)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions."""
    
    def test_create_default_executor(self):
        """Test the create_default_executor function."""
        executor = create_default_executor()
        self.assertIsInstance(executor, SequenceExecutor)
        self.assertIsInstance(executor.control_interface, AcceleratorControlSystemInterface)
        self.assertEqual(executor.state, ExecutionState.IDLE)


if __name__ == '__main__':
    # Ensure we have a QApplication instance
    if not QApplication.instance():
        app = QApplication([])
    
    unittest.main() 