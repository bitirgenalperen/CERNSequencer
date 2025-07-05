"""
PyUI - A Python-based UI framework for CERN accelerator applications.

This package provides a foundation for building PyQt applications with
accelerator-specific components and standardized patterns.
"""

from .application_base import ApplicationBase

__version__ = "0.1.0"
__all__ = ["ApplicationBase", "register_widget", "get_widget", "list_widgets"]

# Widget registry for custom components
_widget_registry = {}

def register_widget(name, widget_class):
    """Register a custom widget class with PyUI.
    
    Args:
        name (str): The name to register the widget under
        widget_class: The widget class to register
    """
    _widget_registry[name] = widget_class

def get_widget(name):
    """Get a registered widget class by name.
    
    Args:
        name (str): The name of the widget to retrieve
        
    Returns:
        The widget class, or None if not found
    """
    return _widget_registry.get(name)

def list_widgets():
    """List all registered widget names.
    
    Returns:
        list: List of registered widget names
    """
    return list(_widget_registry.keys())

# Initialize built-in widgets when the module is imported
def _initialize_builtin_widgets():
    """Initialize built-in PyUI widgets."""
    try:
        from .widgets.example_widget import StyledButton
        register_widget("StyledButton", StyledButton)
    except ImportError:
        pass  # Widgets module not available

# Call initialization
_initialize_builtin_widgets()
