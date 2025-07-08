"""
Accelerator Control System Interface (Mock)

This module provides a mock interface to simulate interactions with CERN's 
particle accelerator control system. It implements placeholder methods for
the various sequence step types supported by the Sequencer UI.

Implementation for Milestone 3 - Development Step 1: Accelerator Control System Interface (Mock)
"""

import time
import random
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum


class ControlSystemStatus(Enum):
    """Status codes for control system operations."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    WARNING = "warning"
    IN_PROGRESS = "in_progress"


class LogLevel(Enum):
    """Log levels for message logging."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AcceleratorControlSystemInterface:
    """
    Mock interface for CERN's accelerator control system.
    
    This class simulates the behavior of the real control system interface
    by printing messages to console and implementing realistic delays.
    All methods are designed to match the parameters expected by the
    sequence step widgets.
    """
    
    def __init__(self):
        """Initialize the mock control system interface."""
        self.connected = True
        self.simulation_mode = True
        self.last_operation_time = None
        self.parameter_store = {}  # Mock parameter storage
        self.event_registry = {}  # Mock event registry
        self.diagnostic_results = {}  # Mock diagnostic results
        self.log_buffer = []  # Mock log buffer
        
        # Initialize with some default parameters
        self._initialize_default_parameters()
        
        print(f"[{self._get_timestamp()}] AcceleratorControlSystemInterface initialized in simulation mode")
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp for logging."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    def _initialize_default_parameters(self):
        """Initialize some default parameters for testing."""
        self.parameter_store = {
            "Magnet_Current_A": 100.5,
            "RF_Frequency_B": 400.12,
            "Beam_Position_X": 0.0,
            "Beam_Position_Y": 0.0,
            "Quadrupole_1": 1.0,
            "Quadrupole_2": 1.2,
            "Steering_Coil_1": 0.5,
            "Vacuum_Pressure": 1e-9,
            "Temperature_Sensor_1": 25.0
        }
        
        # Mock some events that could occur
        self.event_registry = {
            "Beam_Ready_Signal": False,
            "Beam_Position_Stable": False,
            "Vacuum_Ready": True,
            "RF_System_Ready": True,
            "Magnet_System_Ready": True,
            "Emergency_Stop": False,
            "Beam_Dump_Complete": False
        }
    
    def set_parameter(self, name: str, value: Union[str, float, int, bool], 
                     units: str = None, **kwargs) -> Dict[str, Any]:
        """
        Set a parameter in the accelerator control system.
        
        Args:
            name: Parameter name
            value: Parameter value
            units: Optional units specification
            **kwargs: Additional parameters (e.g., timeout, validation)
            
        Returns:
            Dict containing operation result
        """
        start_time = time.time()
        
        print(f"[{self._get_timestamp()}] Setting parameter '{name}' to '{value}'" +
              (f" {units}" if units else ""))
        
        try:
            # Simulate some processing delay
            delay = random.uniform(0.1, 0.5)  # 100-500ms delay
            time.sleep(delay)
            
            # Convert value to appropriate type
            if isinstance(value, str):
                # Try to convert string to number if possible
                try:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    # Keep as string if conversion fails
                    pass
            
            # Store the parameter
            self.parameter_store[name] = value
            self.last_operation_time = time.time()
            
            # Simulate some validation
            if name.startswith("Magnet_") and isinstance(value, (int, float)):
                if value < 0 or value > 1000:
                    print(f"[{self._get_timestamp()}] WARNING: Parameter '{name}' value {value} is outside normal range (0-1000)")
                    return {
                        "status": ControlSystemStatus.WARNING.value,
                        "message": f"Parameter set with warning: value outside normal range",
                        "parameter": name,
                        "value": value,
                        "units": units,
                        "execution_time": time.time() - start_time
                    }
            
            print(f"[{self._get_timestamp()}] Successfully set parameter '{name}' = {value}")
            
            return {
                "status": ControlSystemStatus.SUCCESS.value,
                "message": "Parameter set successfully",
                "parameter": name,
                "value": value,
                "units": units,
                "execution_time": time.time() - start_time
            }
            
        except Exception as e:
            print(f"[{self._get_timestamp()}] ERROR: Failed to set parameter '{name}': {str(e)}")
            return {
                "status": ControlSystemStatus.FAILURE.value,
                "message": f"Failed to set parameter: {str(e)}",
                "parameter": name,
                "value": value,
                "units": units,
                "execution_time": time.time() - start_time
            }
    
    def wait_for_event(self, event_name: str, timeout: float = 30.0,
                      event_source: str = "any", match_criteria: str = "exact",
                      retry_on_timeout: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Wait for a specific event to occur.
        
        Args:
            event_name: Name of the event to wait for
            timeout: Maximum time to wait in seconds
            event_source: Source of the event (optional)
            match_criteria: How to match the event name (optional)
            retry_on_timeout: Whether to retry on timeout (optional)
            **kwargs: Additional parameters
            
        Returns:
            Dict containing operation result
        """
        start_time = time.time()
        
        print(f"[{self._get_timestamp()}] Waiting for event '{event_name}' (timeout: {timeout}s)")
        
        try:
            # Simulate waiting for event
            elapsed = 0
            check_interval = 0.1  # Check every 100ms
            
            while elapsed < timeout:
                # Simulate random event occurrence
                if event_name in self.event_registry:
                    # Simulate the event occurring based on some probability
                    if random.random() < 0.1:  # 10% chance per check
                        self.event_registry[event_name] = True
                        print(f"[{self._get_timestamp()}] Event '{event_name}' occurred!")
                        
                        return {
                            "status": ControlSystemStatus.SUCCESS.value,
                            "message": f"Event '{event_name}' occurred",
                            "event_name": event_name,
                            "wait_time": elapsed,
                            "execution_time": time.time() - start_time
                        }
                
                time.sleep(check_interval)
                elapsed += check_interval
            
            # Timeout occurred
            print(f"[{self._get_timestamp()}] Timeout waiting for event '{event_name}' after {timeout}s")
            
            if retry_on_timeout:
                print(f"[{self._get_timestamp()}] Retrying wait for event '{event_name}'...")
                # In a real implementation, this would retry the operation
                
            return {
                "status": ControlSystemStatus.TIMEOUT.value,
                "message": f"Timeout waiting for event '{event_name}' after {timeout}s",
                "event_name": event_name,
                "wait_time": elapsed,
                "execution_time": time.time() - start_time
            }
            
        except Exception as e:
            print(f"[{self._get_timestamp()}] ERROR: Failed to wait for event '{event_name}': {str(e)}")
            return {
                "status": ControlSystemStatus.FAILURE.value,
                "message": f"Failed to wait for event: {str(e)}",
                "event_name": event_name,
                "execution_time": time.time() - start_time
            }
    
    def delay(self, duration: float, precision: str = "normal", 
              interruptible: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Introduce a delay in sequence execution.
        
        Args:
            duration: Duration of delay in seconds
            precision: Precision of the delay ("normal", "high", "low")
            interruptible: Whether the delay can be interrupted
            **kwargs: Additional parameters
            
        Returns:
            Dict containing operation result
        """
        start_time = time.time()
        
        print(f"[{self._get_timestamp()}] Starting delay of {duration} seconds (precision: {precision})")
        
        try:
            # Adjust actual delay based on precision
            if precision == "high":
                # High precision: very accurate timing
                actual_delay = duration
            elif precision == "low":
                # Low precision: allow some variation
                actual_delay = duration * random.uniform(0.9, 1.1)
            else:
                # Normal precision: slight variation
                actual_delay = duration * random.uniform(0.98, 1.02)
            
            # Simulate the delay
            if interruptible:
                # For interruptible delays, we could check for interruption signals
                # For now, just sleep normally
                time.sleep(actual_delay)
            else:
                time.sleep(actual_delay)
            
            execution_time = time.time() - start_time
            print(f"[{self._get_timestamp()}] Delay completed (actual: {execution_time:.3f}s)")
            
            return {
                "status": ControlSystemStatus.SUCCESS.value,
                "message": f"Delay completed successfully",
                "requested_duration": duration,
                "actual_duration": execution_time,
                "precision": precision,
                "execution_time": execution_time
            }
            
        except Exception as e:
            print(f"[{self._get_timestamp()}] ERROR: Delay failed: {str(e)}")
            return {
                "status": ControlSystemStatus.FAILURE.value,
                "message": f"Delay failed: {str(e)}",
                "requested_duration": duration,
                "execution_time": time.time() - start_time
            }
    
    def run_diagnostic(self, diagnostic_name: str, test_parameters: Dict[str, Any] = None,
                      test_category: str = "system", timeout: float = 60.0,
                      continue_on_failure: bool = False, save_results: bool = True,
                      **kwargs) -> Dict[str, Any]:
        """
        Run a diagnostic test on accelerator components.
        
        Args:
            diagnostic_name: Name of the diagnostic to run
            test_parameters: Parameters for the diagnostic test
            test_category: Category of the test
            timeout: Maximum time to wait for test completion
            continue_on_failure: Whether to continue on test failure
            save_results: Whether to save test results
            **kwargs: Additional parameters
            
        Returns:
            Dict containing operation result and test results
        """
        start_time = time.time()
        
        if test_parameters is None:
            test_parameters = {}
        
        print(f"[{self._get_timestamp()}] Running diagnostic '{diagnostic_name}' (category: {test_category})")
        if test_parameters:
            print(f"[{self._get_timestamp()}] Test parameters: {test_parameters}")
        
        try:
            # Simulate diagnostic execution
            test_duration = random.uniform(1.0, 5.0)  # 1-5 second test
            
            # Show progress
            print(f"[{self._get_timestamp()}] Executing diagnostic test...")
            time.sleep(test_duration)
            
            # Simulate test results
            success_probability = 0.85  # 85% success rate
            test_passed = random.random() < success_probability
            
            # Generate mock test results
            results = {
                "diagnostic_name": diagnostic_name,
                "test_category": test_category,
                "test_passed": test_passed,
                "test_duration": test_duration,
                "test_parameters": test_parameters,
                "timestamp": self._get_timestamp()
            }
            
            if test_passed:
                results["test_results"] = {
                    "status": "PASS",
                    "details": f"Diagnostic '{diagnostic_name}' completed successfully",
                    "metrics": {
                        "response_time": random.uniform(0.1, 1.0),
                        "accuracy": random.uniform(0.95, 1.0),
                        "stability": random.uniform(0.9, 1.0)
                    }
                }
                print(f"[{self._get_timestamp()}] Diagnostic PASSED: {diagnostic_name}")
                status = ControlSystemStatus.SUCCESS
            else:
                results["test_results"] = {
                    "status": "FAIL",
                    "details": f"Diagnostic '{diagnostic_name}' failed - simulated error",
                    "error_code": random.choice(["E001", "E002", "E003"]),
                    "error_message": "Simulated diagnostic failure"
                }
                print(f"[{self._get_timestamp()}] Diagnostic FAILED: {diagnostic_name}")
                status = ControlSystemStatus.FAILURE
            
            # Save results if requested
            if save_results:
                self.diagnostic_results[diagnostic_name] = results
                print(f"[{self._get_timestamp()}] Diagnostic results saved")
            
            return {
                "status": status.value,
                "message": f"Diagnostic '{diagnostic_name}' completed",
                "diagnostic_results": results,
                "execution_time": time.time() - start_time
            }
            
        except Exception as e:
            print(f"[{self._get_timestamp()}] ERROR: Diagnostic '{diagnostic_name}' failed: {str(e)}")
            return {
                "status": ControlSystemStatus.FAILURE.value,
                "message": f"Diagnostic failed: {str(e)}",
                "diagnostic_name": diagnostic_name,
                "execution_time": time.time() - start_time
            }
    
    def log_message(self, message: str, log_level: str = "info", 
                   category: str = "sequence", include_timestamp: bool = True,
                   include_step_info: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Log a message to the accelerator control system.
        
        Args:
            message: Message to log
            log_level: Severity level of the message
            category: Category of the message
            include_timestamp: Whether to include timestamp
            include_step_info: Whether to include step information
            **kwargs: Additional parameters
            
        Returns:
            Dict containing operation result
        """
        start_time = time.time()
        
        try:
            # Validate log level
            try:
                level_enum = LogLevel(log_level.lower())
            except ValueError:
                level_enum = LogLevel.INFO
                log_level = "info"
            
            # Format the log message
            formatted_message = message
            if include_timestamp:
                formatted_message = f"[{self._get_timestamp()}] {formatted_message}"
            
            if include_step_info:
                formatted_message = f"[{category.upper()}] {formatted_message}"
            
            # Print to console with appropriate formatting
            if level_enum == LogLevel.ERROR or level_enum == LogLevel.CRITICAL:
                print(f"ERROR: {formatted_message}")
            elif level_enum == LogLevel.WARNING:
                print(f"WARNING: {formatted_message}")
            elif level_enum == LogLevel.DEBUG:
                print(f"DEBUG: {formatted_message}")
            else:
                print(f"INFO: {formatted_message}")
            
            # Store in log buffer
            log_entry = {
                "message": message,
                "log_level": log_level,
                "category": category,
                "timestamp": self._get_timestamp(),
                "formatted_message": formatted_message
            }
            self.log_buffer.append(log_entry)
            
            # Keep only last 1000 log entries
            if len(self.log_buffer) > 1000:
                self.log_buffer = self.log_buffer[-1000:]
            
            return {
                "status": ControlSystemStatus.SUCCESS.value,
                "message": "Log message recorded successfully",
                "log_entry": log_entry,
                "execution_time": time.time() - start_time
            }
            
        except Exception as e:
            print(f"[{self._get_timestamp()}] ERROR: Failed to log message: {str(e)}")
            return {
                "status": ControlSystemStatus.FAILURE.value,
                "message": f"Failed to log message: {str(e)}",
                "execution_time": time.time() - start_time
            }
    
    def get_parameter(self, name: str) -> Dict[str, Any]:
        """
        Get the current value of a parameter.
        
        Args:
            name: Parameter name
            
        Returns:
            Dict containing parameter value and metadata
        """
        if name in self.parameter_store:
            return {
                "status": ControlSystemStatus.SUCCESS.value,
                "parameter": name,
                "value": self.parameter_store[name],
                "timestamp": self._get_timestamp()
            }
        else:
            return {
                "status": ControlSystemStatus.FAILURE.value,
                "message": f"Parameter '{name}' not found",
                "parameter": name
            }
    
    def get_event_status(self, event_name: str) -> Dict[str, Any]:
        """
        Get the current status of an event.
        
        Args:
            event_name: Event name
            
        Returns:
            Dict containing event status
        """
        if event_name in self.event_registry:
            return {
                "status": ControlSystemStatus.SUCCESS.value,
                "event_name": event_name,
                "event_status": self.event_registry[event_name],
                "timestamp": self._get_timestamp()
            }
        else:
            return {
                "status": ControlSystemStatus.FAILURE.value,
                "message": f"Event '{event_name}' not found",
                "event_name": event_name
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status.
        
        Returns:
            Dict containing system status information
        """
        return {
            "status": ControlSystemStatus.SUCCESS.value,
            "connected": self.connected,
            "simulation_mode": self.simulation_mode,
            "parameters_count": len(self.parameter_store),
            "events_count": len(self.event_registry),
            "diagnostics_count": len(self.diagnostic_results),
            "log_entries_count": len(self.log_buffer),
            "last_operation_time": self.last_operation_time,
            "timestamp": self._get_timestamp()
        }
    
    def reset_system(self) -> Dict[str, Any]:
        """
        Reset the mock system to initial state.
        
        Returns:
            Dict containing reset operation result
        """
        print(f"[{self._get_timestamp()}] Resetting accelerator control system...")
        
        self.parameter_store.clear()
        self.event_registry.clear()
        self.diagnostic_results.clear()
        self.log_buffer.clear()
        self.last_operation_time = None
        
        self._initialize_default_parameters()
        
        print(f"[{self._get_timestamp()}] System reset completed")
        
        return {
            "status": ControlSystemStatus.SUCCESS.value,
            "message": "System reset completed successfully",
            "timestamp": self._get_timestamp()
        }


# Create a default instance that can be imported
default_interface = AcceleratorControlSystemInterface()

# Convenience functions that use the default interface
def set_parameter(name: str, value: Union[str, float, int, bool], **kwargs) -> Dict[str, Any]:
    """Convenience function to set a parameter using the default interface."""
    return default_interface.set_parameter(name, value, **kwargs)

def wait_for_event(event_name: str, timeout: float = 30.0, **kwargs) -> Dict[str, Any]:
    """Convenience function to wait for an event using the default interface."""
    return default_interface.wait_for_event(event_name, timeout, **kwargs)

def delay(duration: float, **kwargs) -> Dict[str, Any]:
    """Convenience function to introduce a delay using the default interface."""
    return default_interface.delay(duration, **kwargs)

def run_diagnostic(diagnostic_name: str, test_parameters: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
    """Convenience function to run a diagnostic using the default interface."""
    return default_interface.run_diagnostic(diagnostic_name, test_parameters, **kwargs)

def log_message(message: str, log_level: str = "info", **kwargs) -> Dict[str, Any]:
    """Convenience function to log a message using the default interface."""
    return default_interface.log_message(message, log_level, **kwargs) 