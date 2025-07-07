"""
Step Widgets Package

Contains all the concrete step widget implementations for the Sequencer UI.
These widgets provide user interfaces for configuring different types of sequence steps.
"""

from .set_parameter_widget import SetParameterWidget
from .wait_for_event_widget import WaitForEventWidget
from .delay_widget import DelayWidget
from .run_diagnostic_widget import RunDiagnosticWidget
from .log_message_widget import LogMessageWidget

__all__ = [
    "SetParameterWidget",
    "WaitForEventWidget", 
    "DelayWidget",
    "RunDiagnosticWidget",
    "LogMessageWidget"
]

# Step widget registry mapping step types to widget classes
STEP_WIDGET_REGISTRY = {
    "SetParameter": SetParameterWidget,
    "WaitForEvent": WaitForEventWidget,
    "Delay": DelayWidget,
    "RunDiagnostic": RunDiagnosticWidget,
    "LogMessage": LogMessageWidget
}

def get_step_widget_class(step_type: str):
    """Get the widget class for a given step type.
    
    Args:
        step_type: The step type name
        
    Returns:
        The widget class, or None if not found
    """
    return STEP_WIDGET_REGISTRY.get(step_type)

def get_available_step_types():
    """Get a list of all available step types.
    
    Returns:
        List of step type names
    """
    return list(STEP_WIDGET_REGISTRY.keys())

def create_step_widget(step_type: str, parent=None):
    """Create a step widget instance for the given step type.
    
    Args:
        step_type: The step type name
        parent: Parent widget
        
    Returns:
        Step widget instance, or None if step type not found
    """
    widget_class = get_step_widget_class(step_type)
    if widget_class:
        return widget_class(parent)
    return None
