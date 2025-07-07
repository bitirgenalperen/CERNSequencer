"""
Unit tests for Sequence Data Model module.
"""

import unittest
import json
import uuid
from datetime import datetime
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sequencer_ui.sequence_data_model import (
    StepType, StepStatus, StepParameter, SequenceStep, SequenceMetadata,
    SequenceData, create_set_parameter_step, create_wait_for_event_step,
    create_delay_step, create_run_diagnostic_step, create_log_message_step,
    create_example_sequence
)


class TestStepType(unittest.TestCase):
    """Test cases for StepType enum."""
    
    def test_step_type_values(self):
        """Test that all expected step types are defined."""
        expected_types = [
            "SetParameter", "WaitForEvent", "Delay", 
            "RunDiagnostic", "LogMessage"
        ]
        
        for expected_type in expected_types:
            self.assertTrue(
                any(step_type.value == expected_type for step_type in StepType),
                f"StepType {expected_type} not found"
            )
    
    def test_step_type_enum_access(self):
        """Test accessing step types by name."""
        self.assertEqual(StepType.SET_PARAMETER.value, "SetParameter")
        self.assertEqual(StepType.WAIT_FOR_EVENT.value, "WaitForEvent")
        self.assertEqual(StepType.DELAY.value, "Delay")


class TestStepStatus(unittest.TestCase):
    """Test cases for StepStatus enum."""
    
    def test_step_status_values(self):
        """Test that all expected step statuses are defined."""
        expected_statuses = [
            "pending", "running", "completed", "failed", "skipped"
        ]
        
        for expected_status in expected_statuses:
            self.assertTrue(
                any(status.value == expected_status for status in StepStatus),
                f"StepStatus {expected_status} not found"
            )


class TestStepParameter(unittest.TestCase):
    """Test cases for StepParameter class."""
    
    def test_step_parameter_creation(self):
        """Test creating a step parameter."""
        param = StepParameter(
            name="test_param",
            value=42,
            data_type="number",
            description="Test parameter"
        )
        
        self.assertEqual(param.name, "test_param")
        self.assertEqual(param.value, 42)
        self.assertEqual(param.data_type, "number")
        self.assertEqual(param.description, "Test parameter")
    
    def test_step_parameter_validation(self):
        """Test step parameter validation."""
        # Valid number parameter
        param = StepParameter(name="num_param", value=42, data_type="number")
        self.assertTrue(param.validate())
        
        # Invalid number parameter
        param = StepParameter(name="num_param", value="not_a_number", data_type="number")
        self.assertFalse(param.validate())
        
        # Valid string parameter
        param = StepParameter(name="str_param", value="hello", data_type="string")
        self.assertTrue(param.validate())
        
        # Valid boolean parameter
        param = StepParameter(name="bool_param", value=True, data_type="boolean")
        self.assertTrue(param.validate())
        
        # Empty name should fail
        param = StepParameter(name="", value="test", data_type="string")
        self.assertFalse(param.validate())


class TestSequenceStep(unittest.TestCase):
    """Test cases for SequenceStep class."""
    
    def test_sequence_step_creation(self):
        """Test creating a sequence step."""
        step = SequenceStep(
            step_type=StepType.SET_PARAMETER,
            parameters={"name": "test_param", "value": 42},
            description="Test step"
        )
        
        self.assertEqual(step.step_type, StepType.SET_PARAMETER)
        self.assertEqual(step.parameters["name"], "test_param")
        self.assertEqual(step.parameters["value"], 42)
        self.assertEqual(step.description, "Test step")
        self.assertTrue(step.enabled)
        self.assertEqual(step.status, StepStatus.PENDING)
    
    def test_sequence_step_validation(self):
        """Test sequence step validation."""
        # Valid SetParameter step
        step = SequenceStep(
            step_type=StepType.SET_PARAMETER,
            parameters={"name": "test_param", "value": 42}
        )
        is_valid, errors = step.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid SetParameter step (missing name)
        step = SequenceStep(
            step_type=StepType.SET_PARAMETER,
            parameters={"value": 42}
        )
        is_valid, errors = step.validate()
        self.assertFalse(is_valid)
        self.assertIn("SetParameter step requires 'name' parameter", errors)
        
        # Valid Delay step
        step = SequenceStep(
            step_type=StepType.DELAY,
            parameters={"duration": 5.0}
        )
        is_valid, errors = step.validate()
        self.assertTrue(is_valid)
        
        # Invalid Delay step (negative duration)
        step = SequenceStep(
            step_type=StepType.DELAY,
            parameters={"duration": -1.0}
        )
        is_valid, errors = step.validate()
        self.assertFalse(is_valid)
        self.assertIn("Delay duration must be positive", errors)
    
    def test_sequence_step_serialization(self):
        """Test step serialization to/from dictionary."""
        step = SequenceStep(
            step_type=StepType.SET_PARAMETER,
            parameters={"name": "test_param", "value": 42},
            description="Test step"
        )
        
        # Convert to dict
        step_dict = step.to_dict()
        self.assertEqual(step_dict["step_type"], "SetParameter")
        self.assertEqual(step_dict["parameters"]["name"], "test_param")
        self.assertEqual(step_dict["status"], "pending")
        
        # Convert back from dict
        restored_step = SequenceStep.from_dict(step_dict)
        self.assertEqual(restored_step.step_type, StepType.SET_PARAMETER)
        self.assertEqual(restored_step.parameters["name"], "test_param")
        self.assertEqual(restored_step.status, StepStatus.PENDING)
    
    def test_sequence_step_clone(self):
        """Test cloning a sequence step."""
        original_step = SequenceStep(
            step_type=StepType.SET_PARAMETER,
            parameters={"name": "test_param", "value": 42},
            description="Test step"
        )
        
        cloned_step = original_step.clone()
        
        # Should have different IDs
        self.assertNotEqual(original_step.step_id, cloned_step.step_id)
        
        # Should have same content
        self.assertEqual(original_step.step_type, cloned_step.step_type)
        self.assertEqual(original_step.parameters, cloned_step.parameters)
        self.assertEqual(original_step.description, cloned_step.description)
        
        # Should reset execution status
        self.assertEqual(cloned_step.status, StepStatus.PENDING)
        self.assertIsNone(cloned_step.execution_time)
        self.assertIsNone(cloned_step.error_message)


class TestSequenceData(unittest.TestCase):
    """Test cases for SequenceData class."""
    
    def test_sequence_data_creation(self):
        """Test creating a sequence data object."""
        metadata = SequenceMetadata(name="Test Sequence", description="A test sequence")
        sequence = SequenceData(metadata=metadata)
        
        self.assertEqual(sequence.metadata.name, "Test Sequence")
        self.assertEqual(sequence.metadata.description, "A test sequence")
        self.assertEqual(len(sequence.steps), 0)
        self.assertIsInstance(sequence.variables, dict)
    
    def test_sequence_add_remove_steps(self):
        """Test adding and removing steps."""
        sequence = SequenceData()
        
        # Add a step
        step = SequenceStep(
            step_type=StepType.SET_PARAMETER,
            parameters={"name": "test_param", "value": 42}
        )
        step_id = sequence.add_step(step)
        
        self.assertEqual(len(sequence.steps), 1)
        self.assertEqual(sequence.steps[0].step_id, step_id)
        
        # Remove the step
        removed = sequence.remove_step(step_id)
        self.assertTrue(removed)
        self.assertEqual(len(sequence.steps), 0)
        
        # Try to remove non-existent step
        removed = sequence.remove_step("non_existent_id")
        self.assertFalse(removed)
    
    def test_sequence_move_step(self):
        """Test moving steps within a sequence."""
        sequence = SequenceData()
        
        # Add multiple steps
        step1 = SequenceStep(step_type=StepType.SET_PARAMETER, parameters={"name": "param1", "value": 1})
        step2 = SequenceStep(step_type=StepType.DELAY, parameters={"duration": 1.0})
        step3 = SequenceStep(step_type=StepType.SET_PARAMETER, parameters={"name": "param2", "value": 2})
        
        step1_id = sequence.add_step(step1)
        step2_id = sequence.add_step(step2)
        step3_id = sequence.add_step(step3)
        
        # Move step1 to position 2 (should become: step2, step3, step1)
        moved = sequence.move_step(step1_id, 2)
        self.assertTrue(moved)
        
        self.assertEqual(sequence.steps[0].step_id, step2_id)
        self.assertEqual(sequence.steps[1].step_id, step3_id)
        self.assertEqual(sequence.steps[2].step_id, step1_id)
    
    def test_sequence_get_methods(self):
        """Test various get methods for sequence data."""
        sequence = SequenceData()
        
        # Add steps of different types and statuses
        step1 = SequenceStep(step_type=StepType.SET_PARAMETER, parameters={"name": "param1", "value": 1})
        step2 = SequenceStep(step_type=StepType.DELAY, parameters={"duration": 1.0})
        step3 = SequenceStep(step_type=StepType.SET_PARAMETER, parameters={"name": "param2", "value": 2})
        step3.status = StepStatus.COMPLETED
        
        step1_id = sequence.add_step(step1)
        step2_id = sequence.add_step(step2)
        step3_id = sequence.add_step(step3)
        
        # Test get_step
        retrieved_step = sequence.get_step(step1_id)
        self.assertEqual(retrieved_step.step_id, step1_id)
        
        # Test get_step_index
        index = sequence.get_step_index(step2_id)
        self.assertEqual(index, 1)
        
        # Test get_steps_by_type
        set_param_steps = sequence.get_steps_by_type(StepType.SET_PARAMETER)
        self.assertEqual(len(set_param_steps), 2)
        
        # Test get_steps_by_status
        completed_steps = sequence.get_steps_by_status(StepStatus.COMPLETED)
        self.assertEqual(len(completed_steps), 1)
        self.assertEqual(completed_steps[0].step_id, step3_id)
    
    def test_sequence_validation(self):
        """Test sequence validation."""
        # Valid sequence
        sequence = SequenceData()
        sequence.metadata.name = "Valid Sequence"
        sequence.add_step(SequenceStep(
            step_type=StepType.SET_PARAMETER,
            parameters={"name": "param1", "value": 1}
        ))
        
        is_valid, errors = sequence.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid sequence (empty name)
        sequence.metadata.name = ""
        is_valid, errors = sequence.validate()
        self.assertFalse(is_valid)
        self.assertIn("Sequence name cannot be empty", errors)
    
    def test_sequence_execution_progress(self):
        """Test execution progress tracking."""
        sequence = SequenceData()
        
        # Add steps with different statuses
        step1 = SequenceStep(step_type=StepType.SET_PARAMETER, parameters={"name": "param1", "value": 1})
        step2 = SequenceStep(step_type=StepType.DELAY, parameters={"duration": 1.0})
        step3 = SequenceStep(step_type=StepType.SET_PARAMETER, parameters={"name": "param2", "value": 2})
        
        step1.status = StepStatus.COMPLETED
        step2.status = StepStatus.RUNNING
        step3.status = StepStatus.PENDING
        
        sequence.add_step(step1)
        sequence.add_step(step2)
        sequence.add_step(step3)
        
        progress = sequence.get_execution_progress()
        
        self.assertEqual(progress["total"], 3)
        self.assertEqual(progress["completed"], 1)
        self.assertEqual(progress["running"], 1)
        self.assertEqual(progress["pending"], 1)
        self.assertEqual(progress["failed"], 0)
        self.assertAlmostEqual(progress["progress"], 33.33, places=2)
    
    def test_sequence_serialization(self):
        """Test sequence serialization to/from JSON."""
        sequence = SequenceData()
        sequence.metadata.name = "Test Sequence"
        sequence.add_step(SequenceStep(
            step_type=StepType.SET_PARAMETER,
            parameters={"name": "param1", "value": 42}
        ))
        
        # Convert to JSON
        json_str = sequence.to_json()
        self.assertIsInstance(json_str, str)
        
        # Parse JSON to verify structure
        data = json.loads(json_str)
        self.assertEqual(data["metadata"]["name"], "Test Sequence")
        self.assertEqual(len(data["steps"]), 1)
        self.assertEqual(data["steps"][0]["step_type"], "SetParameter")
        
        # Convert back from JSON
        restored_sequence = SequenceData.from_json(json_str)
        self.assertEqual(restored_sequence.metadata.name, "Test Sequence")
        self.assertEqual(len(restored_sequence.steps), 1)
        self.assertEqual(restored_sequence.steps[0].step_type, StepType.SET_PARAMETER)
    
    def test_sequence_clone(self):
        """Test cloning a sequence."""
        original_sequence = SequenceData()
        original_sequence.metadata.name = "Original Sequence"
        original_sequence.add_step(SequenceStep(
            step_type=StepType.SET_PARAMETER,
            parameters={"name": "param1", "value": 42}
        ))
        
        cloned_sequence = original_sequence.clone("Cloned Sequence")
        
        # Should have different IDs
        self.assertNotEqual(original_sequence.sequence_id, cloned_sequence.sequence_id)
        
        # Should have new name
        self.assertEqual(cloned_sequence.metadata.name, "Cloned Sequence")
        
        # Should have same number of steps but different step IDs
        self.assertEqual(len(cloned_sequence.steps), len(original_sequence.steps))
        self.assertNotEqual(cloned_sequence.steps[0].step_id, original_sequence.steps[0].step_id)
        
        # Should have same step content
        self.assertEqual(cloned_sequence.steps[0].step_type, original_sequence.steps[0].step_type)
        self.assertEqual(cloned_sequence.steps[0].parameters, original_sequence.steps[0].parameters)


class TestFactoryFunctions(unittest.TestCase):
    """Test cases for step factory functions."""
    
    def test_create_set_parameter_step(self):
        """Test creating a SetParameter step."""
        step = create_set_parameter_step("test_param", 42, "Test parameter")
        
        self.assertEqual(step.step_type, StepType.SET_PARAMETER)
        self.assertEqual(step.parameters["name"], "test_param")
        self.assertEqual(step.parameters["value"], 42)
        self.assertEqual(step.description, "Test parameter")
    
    def test_create_wait_for_event_step(self):
        """Test creating a WaitForEvent step."""
        step = create_wait_for_event_step("test_event", 10.0, "Wait for test event")
        
        self.assertEqual(step.step_type, StepType.WAIT_FOR_EVENT)
        self.assertEqual(step.parameters["event_name"], "test_event")
        self.assertEqual(step.parameters["timeout"], 10.0)
        self.assertEqual(step.description, "Wait for test event")
    
    def test_create_delay_step(self):
        """Test creating a Delay step."""
        step = create_delay_step(5.0, "Wait 5 seconds")
        
        self.assertEqual(step.step_type, StepType.DELAY)
        self.assertEqual(step.parameters["duration"], 5.0)
        self.assertEqual(step.description, "Wait 5 seconds")
    
    def test_create_run_diagnostic_step(self):
        """Test creating a RunDiagnostic step."""
        step = create_run_diagnostic_step("test_diagnostic", {"param1": "value1"}, "Run test diagnostic")
        
        self.assertEqual(step.step_type, StepType.RUN_DIAGNOSTIC)
        self.assertEqual(step.parameters["diagnostic_name"], "test_diagnostic")
        self.assertEqual(step.parameters["param1"], "value1")
        self.assertEqual(step.description, "Run test diagnostic")
    
    def test_create_log_message_step(self):
        """Test creating a LogMessage step."""
        step = create_log_message_step("Test message", "INFO", "Log test message")
        
        self.assertEqual(step.step_type, StepType.LOG_MESSAGE)
        self.assertEqual(step.parameters["message"], "Test message")
        self.assertEqual(step.parameters["level"], "INFO")
        self.assertEqual(step.description, "Log test message")


class TestExampleSequence(unittest.TestCase):
    """Test cases for the example sequence."""
    
    def test_create_example_sequence(self):
        """Test creating the example sequence."""
        sequence = create_example_sequence()
        
        self.assertIsInstance(sequence, SequenceData)
        self.assertEqual(sequence.metadata.name, "Example Beam Setup Sequence")
        self.assertGreater(len(sequence.steps), 0)
        
        # Validate the sequence
        is_valid, errors = sequence.validate()
        self.assertTrue(is_valid, f"Example sequence validation failed: {errors}")
        
        # Check that different step types are present
        step_types = [step.step_type for step in sequence.steps]
        self.assertIn(StepType.SET_PARAMETER, step_types)
        self.assertIn(StepType.DELAY, step_types)
        self.assertIn(StepType.WAIT_FOR_EVENT, step_types)


if __name__ == '__main__':
    unittest.main() 