"""
SetParameter Step Widget

Concrete implementation of a step widget for setting accelerator parameters.
This widget allows users to specify a parameter name and value to be set
during sequence execution.
"""

import sys
import os
from typing import Dict, Any, List

# Add the parent directory to the path so we can import pyui
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox
from PyQt5.QtCore import Qt

try:
    from pyui.pyui.widgets.step_widget_base import ParameterStepWidget
except ImportError:
    # Fallback for testing without PyUI
    from abc import ABC, abstractmethod
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import pyqtSignal
    
    class ParameterStepWidget(QWidget):
        parameters_changed = pyqtSignal(dict)
        validation_changed = pyqtSignal(bool)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self._parameter_name = ""
            self._parameter_value = None


class SetParameterWidget(ParameterStepWidget):
    """
    Step widget for setting accelerator parameters.
    
    This widget allows users to:
    - Specify a parameter name
    - Set a parameter value (string, number, or boolean)
    - Choose the parameter type
    - Add an optional description
    """
    
    def __init__(self, parent=None):
        """Initialize the SetParameter widget."""
        super().__init__(parent)
        
        # Widget-specific attributes
        self._description = ""
        self._units = ""
        
        # UI elements
        self.name_edit = None
        self.value_edit = None
        self.type_combo = None
        self.description_edit = None
        self.units_edit = None
        
        # Create the UI
        self.create_ui()
        
        # Set default values
        self.set_parameter_type("number")  # Default to number type
        
    def get_step_type(self) -> str:
        """Get the step type this widget represents."""
        return "SetParameter"
    
    def get_step_name(self) -> str:
        """Get the human-readable name for this step type."""
        return "Set Parameter"
    
    def get_step_description(self) -> str:
        """Get a description of what this step does."""
        return "Sets a parameter to a specified value in the accelerator control system"
    
    def create_ui(self):
        """Create the UI elements for this step widget."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        
        # Parameter Configuration Group
        param_group = self.create_group_box("Parameter Configuration")
        param_layout = self.create_form_layout()
        
        # Parameter name
        self.name_edit = self.create_line_edit(
            placeholder="e.g., Magnet_Current_A, RF_Frequency_B",
            change_handler=self._on_name_changed
        )
        param_layout.addRow("Parameter Name:", self.name_edit)
        
        # Parameter type
        self.type_combo = self.create_combo_box(
            items=["number", "string", "boolean"],
            current_item="number",
            change_handler=self._on_type_changed
        )
        param_layout.addRow("Parameter Type:", self.type_combo)
        
        # Parameter value
        self.value_edit = self.create_line_edit(
            placeholder="Enter parameter value",
            change_handler=self._on_value_changed
        )
        param_layout.addRow("Parameter Value:", self.value_edit)
        
        # Units (optional)
        self.units_edit = self.create_line_edit(
            placeholder="e.g., A, MHz, V (optional)",
            change_handler=self._on_units_changed
        )
        param_layout.addRow("Units:", self.units_edit)
        
        param_group.setLayout(param_layout)
        main_layout.addWidget(param_group)
        
        # Description Group
        desc_group = self.create_group_box("Description")
        desc_layout = QVBoxLayout()
        
        self.description_edit = self.create_text_edit(
            placeholder="Optional description of what this parameter controls...",
            change_handler=self._on_description_changed
        )
        desc_layout.addWidget(self.description_edit)
        
        desc_group.setLayout(desc_layout)
        main_layout.addWidget(desc_group)
        
        # Add stretch to push content to top
        main_layout.addStretch()
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get the current parameters for this step."""
        # Convert value based on type
        raw_value = self.value_edit.text() if self.value_edit else ""
        converted_value = self._convert_value(raw_value, self.get_parameter_type())
        
        parameters = {
            "name": self.get_parameter_name(),
            "value": converted_value
        }
        
        # Add optional parameters if they have values
        if self._units:
            parameters["units"] = self._units
        
        return parameters
    
    def set_parameters(self, parameters: Dict[str, Any]):
        """Set the parameters for this step."""
        if not parameters:
            return
            
        # Set parameter name
        name = parameters.get("name", "")
        self.set_parameter_name(name)
        if self.name_edit:
            self.name_edit.setText(name)
        
        # Set parameter value
        value = parameters.get("value", "")
        self.set_parameter_value(value)
        if self.value_edit:
            self.value_edit.setText(str(value))
        
        # Set parameter type (try to infer if not specified)
        param_type = parameters.get("type", self._infer_type(value))
        self.set_parameter_type(param_type)
        if self.type_combo:
            self.type_combo.setCurrentText(param_type)
        
        # Set optional parameters
        units = parameters.get("units", "")
        self._units = units
        if self.units_edit:
            self.units_edit.setText(units)
        
        # Emit change signal
        self.emit_parameters_changed()
    
    def validate_parameters(self) -> tuple[bool, List[str]]:
        """Validate the current parameters."""
        errors = []
        
        # Check parameter name
        if not self.get_parameter_name().strip():
            errors.append("Parameter name is required")
        elif not self._is_valid_parameter_name(self.get_parameter_name()):
            errors.append("Parameter name contains invalid characters")
        
        # Check parameter value
        value_text = self.value_edit.text() if self.value_edit else ""
        if not value_text.strip():
            errors.append("Parameter value is required")
        else:
            # Validate value based on type
            param_type = self.get_parameter_type()
            if not self._is_valid_value_for_type(value_text, param_type):
                errors.append(f"Parameter value is not a valid {param_type}")
        
        return len(errors) == 0, errors
    
    def _on_name_changed(self, text: str):
        """Handle parameter name changes."""
        self.set_parameter_name(text)
    
    def _on_value_changed(self, text: str):
        """Handle parameter value changes."""
        converted_value = self._convert_value(text, self.get_parameter_type())
        self.set_parameter_value(converted_value)
    
    def _on_type_changed(self, text: str):
        """Handle parameter type changes."""
        self.set_parameter_type(text)
        
        # Update the value field placeholder based on type
        if self.value_edit:
            placeholders = {
                "number": "e.g., 100.5, -25, 3.14159",
                "string": "e.g., ON, READY, beam_mode_1",
                "boolean": "true or false"
            }
            self.value_edit.setPlaceholderText(placeholders.get(text, "Enter value"))
        
        # Re-validate the current value
        self.emit_parameters_changed()
    
    def _on_description_changed(self):
        """Handle description changes."""
        if self.description_edit:
            self._description = self.description_edit.toPlainText()
            self.emit_parameters_changed()
    
    def _on_units_changed(self, text: str):
        """Handle units changes."""
        self._units = text
        self.emit_parameters_changed()
    
    def _convert_value(self, value_text: str, param_type: str) -> Any:
        """Convert value text to appropriate type."""
        if not value_text.strip():
            return None
            
        try:
            if param_type == "number":
                # Try int first, then float
                if "." in value_text or "e" in value_text.lower():
                    return float(value_text)
                else:
                    return int(value_text)
            elif param_type == "boolean":
                return value_text.lower() in ("true", "1", "yes", "on")
            else:  # string
                return value_text
        except ValueError:
            return value_text  # Return as string if conversion fails
    
    def _infer_type(self, value: Any) -> str:
        """Infer parameter type from value."""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, (int, float)):
            return "number"
        else:
            return "string"
    
    def _is_valid_parameter_name(self, name: str) -> bool:
        """Check if parameter name is valid."""
        if not name.strip():
            return False
        
        # Basic validation: alphanumeric, underscore, dash
        import re
        return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name.strip()))
    
    def _is_valid_value_for_type(self, value_text: str, param_type: str) -> bool:
        """Check if value is valid for the specified type."""
        if not value_text.strip():
            return False
        
        try:
            if param_type == "number":
                float(value_text)  # This covers both int and float
                return True
            elif param_type == "boolean":
                return value_text.lower() in ("true", "false", "1", "0", "yes", "no", "on", "off")
            else:  # string
                return True  # Any string is valid
        except ValueError:
            return False
    
    def get_description(self) -> str:
        """Get the step description."""
        return self._description
    
    def set_description(self, description: str):
        """Set the step description."""
        self._description = description
        if self.description_edit:
            self.description_edit.setPlainText(description)
        self.emit_parameters_changed()
    
    def get_units(self) -> str:
        """Get the parameter units."""
        return self._units
    
    def set_units(self, units: str):
        """Set the parameter units."""
        self._units = units
        if self.units_edit:
            self.units_edit.setText(units)
        self.emit_parameters_changed() 