"""
Sequence Data Model Module

This module defines the data structures and validation logic for operational sequences
within the CERN Sequencer UI application. It provides a standardized way to represent
sequences, steps, and their parameters.

Implementation for Milestone 2 - Development Step 1: Sequence Data Model
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
from enum import Enum


class StepType(Enum):
    """Enumeration of supported sequence step types."""
    SET_PARAMETER = "SetParameter"
    WAIT_FOR_EVENT = "WaitForEvent"
    DELAY = "Delay"
    RUN_DIAGNOSTIC = "RunDiagnostic"
    LOG_MESSAGE = "LogMessage"


class StepStatus(Enum):
    """Enumeration of step execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepParameter:
    """Represents a parameter for a sequence step."""
    name: str
    value: Any
    data_type: str = "string"  # string, number, boolean, etc.
    description: str = ""
    
    def validate(self) -> bool:
        """Validate parameter data."""
        if not self.name:
            return False
        
        # Type validation
        if self.data_type == "number":
            return isinstance(self.value, (int, float))
        elif self.data_type == "boolean":
            return isinstance(self.value, bool)
        elif self.data_type == "string":
            return isinstance(self.value, str)
        
        return True


@dataclass
class SequenceStep:
    """Represents a single step in an operational sequence."""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step_type: StepType = StepType.SET_PARAMETER
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    enabled: bool = True
    timeout: Optional[float] = None  # Timeout in seconds
    retry_count: int = 0
    status: StepStatus = StepStatus.PENDING
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        if isinstance(self.step_type, str):
            try:
                self.step_type = StepType(self.step_type)
            except ValueError:
                raise ValueError(f"Invalid step type: {self.step_type}")
        
        if isinstance(self.status, str):
            try:
                self.status = StepStatus(self.status)
            except ValueError:
                raise ValueError(f"Invalid step status: {self.status}")
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate the step configuration.
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate step type specific parameters
        if self.step_type == StepType.SET_PARAMETER:
            if 'name' not in self.parameters:
                errors.append("SetParameter step requires 'name' parameter")
            if 'value' not in self.parameters:
                errors.append("SetParameter step requires 'value' parameter")
                
        elif self.step_type == StepType.WAIT_FOR_EVENT:
            if 'event_name' not in self.parameters:
                errors.append("WaitForEvent step requires 'event_name' parameter")
            if 'timeout' not in self.parameters:
                errors.append("WaitForEvent step requires 'timeout' parameter")
                
        elif self.step_type == StepType.DELAY:
            if 'duration' not in self.parameters:
                errors.append("Delay step requires 'duration' parameter")
            elif not isinstance(self.parameters['duration'], (int, float)):
                errors.append("Delay duration must be a number")
            elif self.parameters['duration'] <= 0:
                errors.append("Delay duration must be positive")
                
        elif self.step_type == StepType.RUN_DIAGNOSTIC:
            if 'diagnostic_name' not in self.parameters:
                errors.append("RunDiagnostic step requires 'diagnostic_name' parameter")
                
        elif self.step_type == StepType.LOG_MESSAGE:
            if 'message' not in self.parameters:
                errors.append("LogMessage step requires 'message' parameter")
        
        # Validate timeout if specified
        if self.timeout is not None:
            if not isinstance(self.timeout, (int, float)) or self.timeout <= 0:
                errors.append("Timeout must be a positive number")
        
        # Validate retry count
        if not isinstance(self.retry_count, int) or self.retry_count < 0:
            errors.append("Retry count must be a non-negative integer")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary representation."""
        data = asdict(self)
        data['step_type'] = self.step_type.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SequenceStep':
        """Create step from dictionary representation."""
        # Convert string enums back to enum objects
        if 'step_type' in data:
            data['step_type'] = StepType(data['step_type'])
        if 'status' in data:
            data['status'] = StepStatus(data['status'])
        
        return cls(**data)
    
    def clone(self) -> 'SequenceStep':
        """Create a copy of this step with a new ID."""
        data = self.to_dict()
        data['step_id'] = str(uuid.uuid4())
        data['status'] = StepStatus.PENDING.value
        data['execution_time'] = None
        data['error_message'] = None
        return SequenceStep.from_dict(data)


@dataclass
class SequenceMetadata:
    """Metadata for a sequence."""
    name: str = "Untitled Sequence"
    description: str = ""
    version: str = "1.0"
    author: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    category: str = "General"


@dataclass
class SequenceData:
    """
    Main data structure representing an operational sequence.
    
    This class encapsulates all the data needed to define, save, load, and execute
    a sequence of operational steps for particle accelerator control.
    """
    sequence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: SequenceMetadata = field(default_factory=SequenceMetadata)
    steps: List[SequenceStep] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)  # Global sequence variables
    
    def __post_init__(self):
        """Post-initialization setup."""
        if not isinstance(self.metadata, SequenceMetadata):
            if isinstance(self.metadata, dict):
                self.metadata = SequenceMetadata(**self.metadata)
            else:
                self.metadata = SequenceMetadata()
        
        # Ensure all steps are SequenceStep objects
        for i, step in enumerate(self.steps):
            if not isinstance(step, SequenceStep):
                if isinstance(step, dict):
                    self.steps[i] = SequenceStep.from_dict(step)
                else:
                    raise ValueError(f"Invalid step data at index {i}")
    
    def add_step(self, step: Union[SequenceStep, Dict[str, Any]], index: Optional[int] = None) -> str:
        """
        Add a step to the sequence.
        
        Args:
            step: SequenceStep object or dictionary
            index: Position to insert step (None for append)
            
        Returns:
            str: ID of the added step
        """
        if isinstance(step, dict):
            step = SequenceStep.from_dict(step)
        elif not isinstance(step, SequenceStep):
            raise ValueError("Step must be SequenceStep object or dictionary")
        
        if index is None:
            self.steps.append(step)
        else:
            self.steps.insert(index, step)
        
        self._update_modified_time()
        return step.step_id
    
    def remove_step(self, step_id: str) -> bool:
        """
        Remove a step from the sequence.
        
        Args:
            step_id: ID of step to remove
            
        Returns:
            bool: True if step was found and removed
        """
        for i, step in enumerate(self.steps):
            if step.step_id == step_id:
                del self.steps[i]
                self._update_modified_time()
                return True
        return False
    
    def move_step(self, step_id: str, new_index: int) -> bool:
        """
        Move a step to a new position in the sequence.
        
        Args:
            step_id: ID of step to move
            new_index: New position for the step
            
        Returns:
            bool: True if step was found and moved
        """
        step = self.get_step(step_id)
        if step is None:
            return False
        
        # Remove and re-insert at new position
        self.remove_step(step_id)
        self.steps.insert(new_index, step)
        self._update_modified_time()
        return True
    
    def get_step(self, step_id: str) -> Optional[SequenceStep]:
        """
        Get a step by its ID.
        
        Args:
            step_id: ID of step to retrieve
            
        Returns:
            SequenceStep or None if not found
        """
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_step_index(self, step_id: str) -> Optional[int]:
        """
        Get the index of a step by its ID.
        
        Args:
            step_id: ID of step to find
            
        Returns:
            int or None if not found
        """
        for i, step in enumerate(self.steps):
            if step.step_id == step_id:
                return i
        return None
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate the entire sequence.
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate metadata
        if not self.metadata.name.strip():
            errors.append("Sequence name cannot be empty")
        
        # Validate steps
        for i, step in enumerate(self.steps):
            is_valid, step_errors = step.validate()
            if not is_valid:
                for error in step_errors:
                    errors.append(f"Step {i+1}: {error}")
        
        # Check for duplicate step IDs
        step_ids = [step.step_id for step in self.steps]
        if len(step_ids) != len(set(step_ids)):
            errors.append("Duplicate step IDs found")
        
        return len(errors) == 0, errors
    
    def get_enabled_steps(self) -> List[SequenceStep]:
        """Get only the enabled steps in the sequence."""
        return [step for step in self.steps if step.enabled]
    
    def get_steps_by_type(self, step_type: StepType) -> List[SequenceStep]:
        """Get all steps of a specific type."""
        return [step for step in self.steps if step.step_type == step_type]
    
    def get_steps_by_status(self, status: StepStatus) -> List[SequenceStep]:
        """Get all steps with a specific status."""
        return [step for step in self.steps if step.status == status]
    
    def reset_execution_status(self):
        """Reset all steps to pending status."""
        for step in self.steps:
            step.status = StepStatus.PENDING
            step.execution_time = None
            step.error_message = None
        self._update_modified_time()
    
    def get_execution_progress(self) -> Dict[str, Any]:
        """Get execution progress statistics."""
        total_steps = len(self.steps)
        if total_steps == 0:
            return {"total": 0, "completed": 0, "failed": 0, "progress": 0.0}
        
        completed = len(self.get_steps_by_status(StepStatus.COMPLETED))
        failed = len(self.get_steps_by_status(StepStatus.FAILED))
        running = len(self.get_steps_by_status(StepStatus.RUNNING))
        
        return {
            "total": total_steps,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": total_steps - completed - failed - running,
            "progress": (completed + failed) / total_steps * 100.0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert sequence to dictionary representation."""
        return {
            "sequence_id": self.sequence_id,
            "metadata": asdict(self.metadata),
            "steps": [step.to_dict() for step in self.steps],
            "variables": self.variables
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SequenceData':
        """Create sequence from dictionary representation."""
        return cls(**data)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert sequence to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SequenceData':
        """Create sequence from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def clone(self, new_name: str = None) -> 'SequenceData':
        """Create a copy of this sequence with new IDs."""
        data = self.to_dict()
        data['sequence_id'] = str(uuid.uuid4())
        
        if new_name:
            data['metadata']['name'] = new_name
        else:
            data['metadata']['name'] = f"{data['metadata']['name']} (Copy)"
        
        data['metadata']['created_at'] = datetime.now().isoformat()
        data['metadata']['modified_at'] = datetime.now().isoformat()
        
        # Create new step IDs
        for step_data in data['steps']:
            step_data['step_id'] = str(uuid.uuid4())
            step_data['status'] = StepStatus.PENDING.value
            step_data['execution_time'] = None
            step_data['error_message'] = None
        
        return SequenceData.from_dict(data)
    
    def _update_modified_time(self):
        """Update the modified timestamp."""
        self.metadata.modified_at = datetime.now().isoformat()


# Factory functions for creating common step types
def create_set_parameter_step(parameter_name: str, value: Any, 
                            description: str = "", **kwargs) -> SequenceStep:
    """Create a SetParameter step."""
    return SequenceStep(
        step_type=StepType.SET_PARAMETER,
        parameters={
            'name': parameter_name,
            'value': value
        },
        description=description or f"Set {parameter_name} to {value}",
        **kwargs
    )


def create_wait_for_event_step(event_name: str, timeout: float = 30.0,
                             description: str = "", **kwargs) -> SequenceStep:
    """Create a WaitForEvent step."""
    return SequenceStep(
        step_type=StepType.WAIT_FOR_EVENT,
        parameters={
            'event_name': event_name,
            'timeout': timeout
        },
        description=description or f"Wait for {event_name} (timeout: {timeout}s)",
        **kwargs
    )


def create_delay_step(duration: float, description: str = "", **kwargs) -> SequenceStep:
    """Create a Delay step."""
    return SequenceStep(
        step_type=StepType.DELAY,
        parameters={
            'duration': duration
        },
        description=description or f"Delay for {duration} seconds",
        **kwargs
    )


def create_run_diagnostic_step(diagnostic_name: str, parameters: Dict[str, Any] = None,
                             description: str = "", **kwargs) -> SequenceStep:
    """Create a RunDiagnostic step."""
    step_params = {'diagnostic_name': diagnostic_name}
    if parameters:
        step_params.update(parameters)
    
    return SequenceStep(
        step_type=StepType.RUN_DIAGNOSTIC,
        parameters=step_params,
        description=description or f"Run diagnostic: {diagnostic_name}",
        **kwargs
    )


def create_log_message_step(message: str, level: str = "INFO", 
                          description: str = "", **kwargs) -> SequenceStep:
    """Create a LogMessage step."""
    return SequenceStep(
        step_type=StepType.LOG_MESSAGE,
        parameters={
            'message': message,
            'level': level
        },
        description=description or f"Log: {message}",
        **kwargs
    )


# Example sequence creation
def create_example_sequence() -> SequenceData:
    """Create an example sequence for testing and demonstration."""
    metadata = SequenceMetadata(
        name="Example Beam Setup Sequence",
        description="A sample sequence for setting up particle beam parameters",
        author="CERN Sequencer UI",
        category="Beam Setup",
        tags=["example", "beam", "setup"]
    )
    
    sequence = SequenceData(metadata=metadata)
    
    # Add example steps
    sequence.add_step(create_set_parameter_step(
        "Magnet_Current_A", 100.5,
        description="Set main magnet current to operational level"
    ))
    
    sequence.add_step(create_delay_step(
        2.0,
        description="Wait for magnet field to stabilize"
    ))
    
    sequence.add_step(create_set_parameter_step(
        "RF_Frequency_B", 400.12,
        description="Set RF frequency for beam acceleration"
    ))
    
    sequence.add_step(create_wait_for_event_step(
        "Beam_Ready_Signal", 10.0,
        description="Wait for beam ready confirmation"
    ))
    
    sequence.add_step(create_run_diagnostic_step(
        "Beam_Position_Check",
        {"tolerance": 0.1, "max_iterations": 5},
        description="Verify beam position within tolerance"
    ))
    
    sequence.add_step(create_log_message_step(
        "Beam setup sequence completed successfully",
        level="INFO",
        description="Log completion status"
    ))
    
    return sequence 