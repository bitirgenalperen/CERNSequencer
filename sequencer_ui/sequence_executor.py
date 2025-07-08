"""
Sequence Executor Module

This module provides the SequenceExecutor class responsible for executing operational
sequences by calling the appropriate methods on the AcceleratorControlSystemInterface.

Implementation for Milestone 3 - Development Step 2: Sequence Executor Logic
"""

import time
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum

from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt5.QtWidgets import QApplication

from .sequence_data_model import (
    SequenceData, 
    SequenceStep, 
    StepType, 
    StepStatus
)
from .accelerator_control_interface import (
    AcceleratorControlSystemInterface,
    ControlSystemStatus
)


class ExecutionState(Enum):
    """Enumeration of sequence execution states."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionMode(Enum):
    """Enumeration of execution modes."""
    NORMAL = "normal"          # Execute all steps
    STEP_BY_STEP = "step_by_step"  # Execute one step at a time
    DRY_RUN = "dry_run"        # Validate without executing


class SequenceExecutor(QObject):
    """
    Executor for operational sequences.
    
    This class is responsible for executing sequences by iterating through
    steps and calling the appropriate methods on the AcceleratorControlSystemInterface.
    It provides comprehensive status updates, error handling, and execution control.
    """
    
    # PyQt signals for UI updates
    execution_started = pyqtSignal(str)  # sequence_id
    execution_completed = pyqtSignal(str, bool)  # sequence_id, success
    execution_paused = pyqtSignal(str)  # sequence_id
    execution_resumed = pyqtSignal(str)  # sequence_id
    execution_stopped = pyqtSignal(str)  # sequence_id
    execution_failed = pyqtSignal(str, str)  # sequence_id, error_message
    
    step_started = pyqtSignal(str, str, int)  # sequence_id, step_id, step_index
    step_completed = pyqtSignal(str, str, bool, float)  # sequence_id, step_id, success, execution_time
    step_failed = pyqtSignal(str, str, str)  # sequence_id, step_id, error_message
    step_skipped = pyqtSignal(str, str, str)  # sequence_id, step_id, reason
    
    progress_updated = pyqtSignal(str, int, int, float)  # sequence_id, current_step, total_steps, progress_percent
    status_message = pyqtSignal(str)  # status_message
    
    def __init__(self, control_interface: AcceleratorControlSystemInterface = None):
        """
        Initialize the sequence executor.
        
        Args:
            control_interface: Interface to the accelerator control system
        """
        super().__init__()
        
        # Control interface
        self.control_interface = control_interface or AcceleratorControlSystemInterface()
        
        # Execution state
        self.state = ExecutionState.IDLE
        self.mode = ExecutionMode.NORMAL
        self.current_sequence: Optional[SequenceData] = None
        self.current_step_index = 0
        self.current_step: Optional[SequenceStep] = None
        
        # Execution control
        self.stop_requested = False
        self.pause_requested = False
        self.step_by_step_mode = False
        self.continue_on_error = False
        
        # Execution statistics
        self.execution_start_time: Optional[float] = None
        self.execution_end_time: Optional[float] = None
        self.total_steps_executed = 0
        self.successful_steps = 0
        self.failed_steps = 0
        self.skipped_steps = 0
        
        # Threading for non-blocking execution
        self.execution_thread: Optional[QThread] = None
        
        # Step validation callbacks
        self.step_validators: Dict[StepType, Callable] = {}
        
        # Initialize step validators
        self._initialize_step_validators()
    
    def _initialize_step_validators(self):
        """Initialize step validation callbacks."""
        self.step_validators = {
            StepType.SET_PARAMETER: self._validate_set_parameter_step,
            StepType.WAIT_FOR_EVENT: self._validate_wait_for_event_step,
            StepType.DELAY: self._validate_delay_step,
            StepType.RUN_DIAGNOSTIC: self._validate_run_diagnostic_step,
            StepType.LOG_MESSAGE: self._validate_log_message_step
        }
    
    def execute_sequence(self, sequence: SequenceData, 
                        mode: ExecutionMode = ExecutionMode.NORMAL,
                        continue_on_error: bool = False) -> bool:
        """
        Execute a sequence of steps.
        
        Args:
            sequence: The sequence to execute
            mode: Execution mode (normal, step-by-step, dry-run)
            continue_on_error: Whether to continue execution after errors
            
        Returns:
            bool: True if execution started successfully, False otherwise
        """
        if self.state != ExecutionState.IDLE:
            self.status_message.emit(f"Cannot start execution: executor is {self.state.value}")
            return False
        
        # Validate sequence
        is_valid, errors = sequence.validate()
        if not is_valid:
            error_msg = f"Sequence validation failed: {'; '.join(errors)}"
            self.status_message.emit(error_msg)
            self.execution_failed.emit(sequence.sequence_id, error_msg)
            return False
        
        # Reset execution state
        self._reset_execution_state()
        
        # Setup execution
        self.current_sequence = sequence
        self.mode = mode
        self.continue_on_error = continue_on_error
        self.state = ExecutionState.RUNNING
        
        # Reset step statuses
        sequence.reset_execution_status()
        
        # Start execution in separate thread for non-blocking operation
        if mode == ExecutionMode.DRY_RUN:
            # Dry run can be synchronous
            return self._execute_dry_run()
        else:
            # Normal execution should be asynchronous
            self.execution_thread = SequenceExecutionThread(self)
            self.execution_thread.finished.connect(self._on_execution_thread_finished)
            self.execution_thread.start()
            return True
    
    def _execute_dry_run(self) -> bool:
        """
        Execute a dry run (validation only) of the sequence.
        
        Returns:
            bool: True if validation passed, False otherwise
        """
        try:
            self.execution_started.emit(self.current_sequence.sequence_id)
            self.status_message.emit("Starting dry run validation...")
            
            enabled_steps = self.current_sequence.get_enabled_steps()
            total_steps = len(enabled_steps)
            
            for i, step in enumerate(enabled_steps):
                # Validate step
                is_valid, errors = self._validate_step(step)
                if not is_valid:
                    error_msg = f"Step {i+1} validation failed: {'; '.join(errors)}"
                    self.step_failed.emit(self.current_sequence.sequence_id, step.step_id, error_msg)
                    if not self.continue_on_error:
                        self.execution_failed.emit(self.current_sequence.sequence_id, error_msg)
                        return False
                
                # Update progress
                progress = (i + 1) / total_steps * 100.0
                self.progress_updated.emit(
                    self.current_sequence.sequence_id, 
                    i + 1, 
                    total_steps, 
                    progress
                )
            
            self.status_message.emit("Dry run completed successfully")
            self.execution_completed.emit(self.current_sequence.sequence_id, True)
            return True
            
        except Exception as e:
            error_msg = f"Dry run failed: {str(e)}"
            self.status_message.emit(error_msg)
            self.execution_failed.emit(self.current_sequence.sequence_id, error_msg)
            return False
        finally:
            self.state = ExecutionState.IDLE
    
    def _execute_sequence_steps(self):
        """Execute the sequence steps (called from execution thread)."""
        try:
            self.execution_start_time = time.time()
            
            # Emit execution started signal
            self.execution_started.emit(self.current_sequence.sequence_id)
            self.status_message.emit(f"Starting execution of sequence '{self.current_sequence.metadata.name}'")
            
            # Get enabled steps
            enabled_steps = self.current_sequence.get_enabled_steps()
            total_steps = len(enabled_steps)
            
            if total_steps == 0:
                self.status_message.emit("No enabled steps to execute")
                self.execution_completed.emit(self.current_sequence.sequence_id, True)
                return
            
            # Execute each step
            for i, step in enumerate(enabled_steps):
                # Check for stop/pause requests
                if self.stop_requested:
                    self.status_message.emit("Execution stopped by user")
                    self.execution_stopped.emit(self.current_sequence.sequence_id)
                    return
                
                if self.pause_requested:
                    self.state = ExecutionState.PAUSED
                    self.execution_paused.emit(self.current_sequence.sequence_id)
                    self.status_message.emit("Execution paused")
                    
                    # Wait for resume
                    while self.pause_requested and not self.stop_requested:
                        QApplication.processEvents()
                        time.sleep(0.1)
                    
                    if self.stop_requested:
                        self.execution_stopped.emit(self.current_sequence.sequence_id)
                        return
                    
                    # Resume execution
                    self.state = ExecutionState.RUNNING
                    self.execution_resumed.emit(self.current_sequence.sequence_id)
                    self.status_message.emit("Execution resumed")
                
                # Execute the step
                self.current_step_index = i
                self.current_step = step
                success = self._execute_step(step, i + 1, total_steps)
                
                if not success and not self.continue_on_error:
                    error_msg = f"Execution failed at step {i + 1}: {step.error_message}"
                    self.status_message.emit(error_msg)
                    self.execution_failed.emit(self.current_sequence.sequence_id, error_msg)
                    return
                
                # Step-by-step mode: wait for user input
                if self.mode == ExecutionMode.STEP_BY_STEP and i < total_steps - 1:
                    self.status_message.emit("Step-by-step mode: waiting for continue signal")
                    # In a real implementation, this would wait for a signal
                    # For now, we'll just add a small delay
                    time.sleep(0.5)
            
            # Execution completed successfully
            self.execution_end_time = time.time()
            execution_time = self.execution_end_time - self.execution_start_time
            
            self.status_message.emit(
                f"Sequence execution completed in {execution_time:.2f}s "
                f"({self.successful_steps} successful, {self.failed_steps} failed, {self.skipped_steps} skipped)"
            )
            self.execution_completed.emit(self.current_sequence.sequence_id, True)
            
        except Exception as e:
            error_msg = f"Execution failed with exception: {str(e)}"
            self.status_message.emit(error_msg)
            self.execution_failed.emit(self.current_sequence.sequence_id, error_msg)
        finally:
            self.state = ExecutionState.COMPLETED if self.failed_steps == 0 else ExecutionState.FAILED
    
    def _execute_step(self, step: SequenceStep, step_number: int, total_steps: int) -> bool:
        """
        Execute a single step.
        
        Args:
            step: The step to execute
            step_number: Current step number (1-based)
            total_steps: Total number of steps
            
        Returns:
            bool: True if step executed successfully, False otherwise
        """
        try:
            # Update step status to running
            step.status = StepStatus.RUNNING
            step_start_time = time.time()
            
            # Emit step started signal
            self.step_started.emit(
                self.current_sequence.sequence_id, 
                step.step_id, 
                step_number - 1
            )
            
            step_description = f"Step {step_number}/{total_steps}: {step.step_type.value}"
            if step.description:
                step_description += f" - {step.description}"
            
            self.status_message.emit(f"Executing {step_description}")
            
            # Validate step before execution
            is_valid, errors = self._validate_step(step)
            if not is_valid:
                error_msg = f"Step validation failed: {'; '.join(errors)}"
                step.error_message = error_msg
                step.status = StepStatus.FAILED
                self.step_failed.emit(self.current_sequence.sequence_id, step.step_id, error_msg)
                self.failed_steps += 1
                return False
            
            # Execute step based on type
            result = self._execute_step_by_type(step)
            
            # Calculate execution time
            step.execution_time = time.time() - step_start_time
            
            # Update step status based on result
            if result and result.get("status") == ControlSystemStatus.SUCCESS.value:
                step.status = StepStatus.COMPLETED
                self.step_completed.emit(
                    self.current_sequence.sequence_id, 
                    step.step_id, 
                    True, 
                    step.execution_time
                )
                self.successful_steps += 1
                success = True
            elif result and result.get("status") == ControlSystemStatus.WARNING.value:
                # Treat warnings as success but log the warning
                step.status = StepStatus.COMPLETED
                warning_msg = result.get("message", "Unknown warning")
                self.status_message.emit(f"Warning: {warning_msg}")
                self.step_completed.emit(
                    self.current_sequence.sequence_id, 
                    step.step_id, 
                    True, 
                    step.execution_time
                )
                self.successful_steps += 1
                success = True
            else:
                # Handle failure
                error_msg = result.get("message", "Unknown error") if result else "No result returned"
                step.error_message = error_msg
                step.status = StepStatus.FAILED
                self.step_failed.emit(self.current_sequence.sequence_id, step.step_id, error_msg)
                self.failed_steps += 1
                success = False
            
            # Update progress
            progress = step_number / total_steps * 100.0
            self.progress_updated.emit(
                self.current_sequence.sequence_id, 
                step_number, 
                total_steps, 
                progress
            )
            
            self.total_steps_executed += 1
            return success
            
        except Exception as e:
            # Handle unexpected exceptions
            error_msg = f"Unexpected error executing step: {str(e)}"
            step.error_message = error_msg
            step.status = StepStatus.FAILED
            step.execution_time = time.time() - step_start_time if 'step_start_time' in locals() else 0
            
            self.step_failed.emit(self.current_sequence.sequence_id, step.step_id, error_msg)
            self.failed_steps += 1
            return False
    
    def _execute_step_by_type(self, step: SequenceStep) -> Dict[str, Any]:
        """
        Execute a step based on its type.
        
        Args:
            step: The step to execute
            
        Returns:
            Dict containing the execution result
        """
        try:
            if step.step_type == StepType.SET_PARAMETER:
                return self._execute_set_parameter_step(step)
            elif step.step_type == StepType.WAIT_FOR_EVENT:
                return self._execute_wait_for_event_step(step)
            elif step.step_type == StepType.DELAY:
                return self._execute_delay_step(step)
            elif step.step_type == StepType.RUN_DIAGNOSTIC:
                return self._execute_run_diagnostic_step(step)
            elif step.step_type == StepType.LOG_MESSAGE:
                return self._execute_log_message_step(step)
            else:
                return {
                    "status": ControlSystemStatus.FAILURE.value,
                    "message": f"Unknown step type: {step.step_type}"
                }
        except Exception as e:
            return {
                "status": ControlSystemStatus.FAILURE.value,
                "message": f"Exception executing step: {str(e)}"
            }
    
    def _execute_set_parameter_step(self, step: SequenceStep) -> Dict[str, Any]:
        """Execute a SetParameter step."""
        params = step.parameters
        return self.control_interface.set_parameter(
            name=params["name"],
            value=params["value"],
            units=params.get("units"),
            timeout=step.timeout
        )
    
    def _execute_wait_for_event_step(self, step: SequenceStep) -> Dict[str, Any]:
        """Execute a WaitForEvent step."""
        params = step.parameters
        timeout = params.get("timeout", step.timeout or 30.0)
        
        return self.control_interface.wait_for_event(
            event_name=params["event_name"],
            timeout=timeout,
            event_source=params.get("event_source", "any"),
            match_criteria=params.get("match_criteria", "exact"),
            retry_on_timeout=params.get("retry_on_timeout", False)
        )
    
    def _execute_delay_step(self, step: SequenceStep) -> Dict[str, Any]:
        """Execute a Delay step."""
        params = step.parameters
        return self.control_interface.delay(
            duration=params["duration"],
            precision=params.get("precision", "normal"),
            interruptible=params.get("interruptible", True)
        )
    
    def _execute_run_diagnostic_step(self, step: SequenceStep) -> Dict[str, Any]:
        """Execute a RunDiagnostic step."""
        params = step.parameters
        return self.control_interface.run_diagnostic(
            diagnostic_name=params["diagnostic_name"],
            test_parameters=params.get("test_parameters", {}),
            test_category=params.get("test_category", "system"),
            timeout=step.timeout or 60.0,
            continue_on_failure=params.get("continue_on_failure", False),
            save_results=params.get("save_results", True)
        )
    
    def _execute_log_message_step(self, step: SequenceStep) -> Dict[str, Any]:
        """Execute a LogMessage step."""
        params = step.parameters
        return self.control_interface.log_message(
            message=params["message"],
            log_level=params.get("log_level", "info"),
            category=params.get("category", "sequence"),
            include_timestamp=params.get("include_timestamp", True),
            include_step_info=params.get("include_step_info", True)
        )
    
    def _validate_step(self, step: SequenceStep) -> tuple[bool, List[str]]:
        """
        Validate a step before execution.
        
        Args:
            step: The step to validate
            
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        # First, use the step's built-in validation
        is_valid, errors = step.validate()
        
        # Then, use step-type-specific validation
        if step.step_type in self.step_validators:
            step_is_valid, step_errors = self.step_validators[step.step_type](step)
            is_valid = is_valid and step_is_valid
            errors.extend(step_errors)
        
        return is_valid, errors
    
    def _validate_set_parameter_step(self, step: SequenceStep) -> tuple[bool, List[str]]:
        """Validate a SetParameter step."""
        errors = []
        params = step.parameters
        
        # Check if parameter name is valid
        if not isinstance(params.get("name"), str) or not params["name"].strip():
            errors.append("Parameter name must be a non-empty string")
        
        # Check if value is provided
        if "value" not in params:
            errors.append("Parameter value is required")
        
        return len(errors) == 0, errors
    
    def _validate_wait_for_event_step(self, step: SequenceStep) -> tuple[bool, List[str]]:
        """Validate a WaitForEvent step."""
        errors = []
        params = step.parameters
        
        # Check event name
        if not isinstance(params.get("event_name"), str) or not params["event_name"].strip():
            errors.append("Event name must be a non-empty string")
        
        # Check timeout
        timeout = params.get("timeout", 30.0)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            errors.append("Timeout must be a positive number")
        
        return len(errors) == 0, errors
    
    def _validate_delay_step(self, step: SequenceStep) -> tuple[bool, List[str]]:
        """Validate a Delay step."""
        errors = []
        params = step.parameters
        
        # Check duration
        duration = params.get("duration")
        if not isinstance(duration, (int, float)) or duration <= 0:
            errors.append("Delay duration must be a positive number")
        
        # Check precision
        precision = params.get("precision", "normal")
        if precision not in ["high", "normal", "low"]:
            errors.append("Precision must be 'high', 'normal', or 'low'")
        
        return len(errors) == 0, errors
    
    def _validate_run_diagnostic_step(self, step: SequenceStep) -> tuple[bool, List[str]]:
        """Validate a RunDiagnostic step."""
        errors = []
        params = step.parameters
        
        # Check diagnostic name
        if not isinstance(params.get("diagnostic_name"), str) or not params["diagnostic_name"].strip():
            errors.append("Diagnostic name must be a non-empty string")
        
        return len(errors) == 0, errors
    
    def _validate_log_message_step(self, step: SequenceStep) -> tuple[bool, List[str]]:
        """Validate a LogMessage step."""
        errors = []
        params = step.parameters
        
        # Check message
        if not isinstance(params.get("message"), str) or not params["message"].strip():
            errors.append("Log message must be a non-empty string")
        
        # Check log level
        log_level = params.get("log_level", "info")
        valid_levels = ["debug", "info", "warning", "error", "critical"]
        if log_level.lower() not in valid_levels:
            errors.append(f"Log level must be one of: {', '.join(valid_levels)}")
        
        return len(errors) == 0, errors
    
    def pause_execution(self):
        """Pause the currently running execution."""
        if self.state == ExecutionState.RUNNING:
            self.pause_requested = True
            self.status_message.emit("Pause requested...")
    
    def resume_execution(self):
        """Resume paused execution."""
        if self.state == ExecutionState.PAUSED:
            self.pause_requested = False
            self.status_message.emit("Resume requested...")
    
    def stop_execution(self):
        """Stop the currently running execution."""
        if self.state in [ExecutionState.RUNNING, ExecutionState.PAUSED]:
            self.stop_requested = True
            self.status_message.emit("Stop requested...")
    
    def get_execution_status(self) -> Dict[str, Any]:
        """
        Get the current execution status.
        
        Returns:
            Dict containing execution status information
        """
        status = {
            "state": self.state.value,
            "mode": self.mode.value,
            "sequence_id": self.current_sequence.sequence_id if self.current_sequence else None,
            "sequence_name": self.current_sequence.metadata.name if self.current_sequence else None,
            "current_step_index": self.current_step_index,
            "current_step_id": self.current_step.step_id if self.current_step else None,
            "total_steps_executed": self.total_steps_executed,
            "successful_steps": self.successful_steps,
            "failed_steps": self.failed_steps,
            "skipped_steps": self.skipped_steps,
            "execution_start_time": self.execution_start_time,
            "execution_end_time": self.execution_end_time
        }
        
        if self.current_sequence:
            progress = self.current_sequence.get_execution_progress()
            status.update(progress)
        
        return status
    
    def _reset_execution_state(self):
        """Reset execution state for a new execution."""
        self.state = ExecutionState.IDLE
        self.current_sequence = None
        self.current_step_index = 0
        self.current_step = None
        self.stop_requested = False
        self.pause_requested = False
        self.execution_start_time = None
        self.execution_end_time = None
        self.total_steps_executed = 0
        self.successful_steps = 0
        self.failed_steps = 0
        self.skipped_steps = 0
    
    def _on_execution_thread_finished(self):
        """Handle execution thread completion."""
        if self.execution_thread:
            self.execution_thread.deleteLater()
            self.execution_thread = None


class SequenceExecutionThread(QThread):
    """
    Thread for executing sequences without blocking the UI.
    """
    
    def __init__(self, executor: SequenceExecutor):
        """
        Initialize the execution thread.
        
        Args:
            executor: The sequence executor instance
        """
        super().__init__()
        self.executor = executor
    
    def run(self):
        """Execute the sequence in the thread."""
        try:
            self.executor._execute_sequence_steps()
        except Exception as e:
            # Handle any unexpected exceptions
            error_msg = f"Execution thread failed: {str(e)}"
            if self.executor.current_sequence:
                self.executor.execution_failed.emit(
                    self.executor.current_sequence.sequence_id, 
                    error_msg
                )
            self.executor.status_message.emit(error_msg)
        finally:
            # Ensure state is properly set
            if self.executor.state == ExecutionState.RUNNING:
                self.executor.state = ExecutionState.COMPLETED


# Convenience function for creating a default executor
def create_default_executor() -> SequenceExecutor:
    """
    Create a default sequence executor with a default control interface.
    
    Returns:
        SequenceExecutor: A new executor instance
    """
    return SequenceExecutor() 