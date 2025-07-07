"""
Delay Step Widget

Concrete implementation of a step widget for introducing delays in sequences.
This widget allows users to specify a duration for pausing sequence execution.
"""

import sys
import os
from typing import Dict, Any, List

# Add the parent directory to the path so we can import pyui
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QButtonGroup, QRadioButton
from PyQt5.QtCore import Qt

try:
    from pyui.pyui.widgets.step_widget_base import TimingStepWidget
except ImportError:
    # Fallback for testing without PyUI
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import pyqtSignal
    
    class TimingStepWidget(QWidget):
        parameters_changed = pyqtSignal(dict)
        validation_changed = pyqtSignal(bool)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self._duration = 0.0


class DelayWidget(TimingStepWidget):
    """
    Step widget for introducing delays in sequences.
    
    This widget allows users to:
    - Specify a delay duration
    - Choose time units (seconds, minutes, hours)
    - Set delay precision
    - Add an optional description
    """
    
    def __init__(self, parent=None):
        """Initialize the Delay widget."""
        super().__init__(parent)
        
        # Widget-specific attributes
        self._description = ""
        self._time_unit = "seconds"
        self._precision = "normal"
        self._interruptible = True
        
        # UI elements
        self.duration_spinbox = None
        self.unit_combo = None
        self.precision_combo = None
        self.interruptible_checkbox = None
        self.description_edit = None
        self.quick_buttons = []
        
        # Create the UI
        self.create_ui()
        
        # Set default values
        self._duration = 1.0  # Default 1 second delay
        
    def get_step_type(self) -> str:
        """Get the step type this widget represents."""
        return "Delay"
    
    def get_step_name(self) -> str:
        """Get the human-readable name for this step type."""
        return "Delay"
    
    def get_step_description(self) -> str:
        """Get a description of what this step does."""
        return "Introduces a timed delay in sequence execution"
    
    def create_ui(self):
        """Create the UI elements for this step widget."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        
        # Duration Configuration Group
        duration_group = self.create_group_box("Duration Configuration")
        duration_layout = self.create_form_layout()
        
        # Duration value
        self.duration_spinbox = self.create_double_spin_box(
            minimum=0.001,
            maximum=86400.0,  # Max 24 hours in seconds
            value=1.0,
            decimals=3,
            change_handler=self._on_duration_changed
        )
        duration_layout.addRow("Duration:", self.duration_spinbox)
        
        # Time unit
        self.unit_combo = self.create_combo_box(
            items=["seconds", "minutes", "hours"],
            current_item="seconds",
            change_handler=self._on_unit_changed
        )
        duration_layout.addRow("Time Unit:", self.unit_combo)
        
        duration_group.setLayout(duration_layout)
        main_layout.addWidget(duration_group)
        
        # Quick Duration Buttons
        quick_group = self.create_group_box("Quick Durations")
        quick_layout = QHBoxLayout()
        
        quick_durations = [
            ("0.1s", 0.1, "seconds"),
            ("0.5s", 0.5, "seconds"),
            ("1s", 1.0, "seconds"),
            ("2s", 2.0, "seconds"),
            ("5s", 5.0, "seconds"),
            ("10s", 10.0, "seconds"),
            ("30s", 30.0, "seconds"),
            ("1min", 1.0, "minutes"),
            ("5min", 5.0, "minutes")
        ]
        
        for label, value, unit in quick_durations:
            btn = self.create_button(label, lambda v=value, u=unit: self._set_quick_duration(v, u))
            btn.setMaximumWidth(50)
            quick_layout.addWidget(btn)
            self.quick_buttons.append(btn)
        
        quick_layout.addStretch()
        quick_group.setLayout(quick_layout)
        main_layout.addWidget(quick_group)
        
        # Options Group
        options_group = self.create_group_box("Options")
        options_layout = self.create_form_layout()
        
        # Precision
        self.precision_combo = self.create_combo_box(
            items=["low", "normal", "high", "precise"],
            current_item="normal",
            change_handler=self._on_precision_changed
        )
        options_layout.addRow("Precision:", self.precision_combo)
        
        # Interruptible
        self.interruptible_checkbox = self.create_checkbox(
            "Allow interruption",
            checked=True,
            change_handler=self._on_interruptible_changed
        )
        options_layout.addRow("", self.interruptible_checkbox)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Description Group
        desc_group = self.create_group_box("Description")
        desc_layout = QVBoxLayout()
        
        self.description_edit = self.create_text_edit(
            placeholder="Optional description of why this delay is needed...",
            change_handler=self._on_description_changed
        )
        desc_layout.addWidget(self.description_edit)
        
        desc_group.setLayout(desc_layout)
        main_layout.addWidget(desc_group)
        
        # Add stretch to push content to top
        main_layout.addStretch()
    
    def create_button(self, text, handler):
        """Create a styled button for quick durations."""
        try:
            from pyui.pyui import get_widget
            StyledButton = get_widget("StyledButton")
            if StyledButton:
                btn = StyledButton(text)
                btn.set_size("small")
                btn.clicked.connect(handler)
                return btn
        except ImportError:
            pass
        
        # Fallback to regular button
        from PyQt5.QtWidgets import QPushButton
        btn = QPushButton(text)
        btn.clicked.connect(handler)
        return btn
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get the current parameters for this step."""
        # Always return the internal duration value, not the UI display value
        # This ensures we get the actual stored value even if it's outside UI limits
        parameters = {
            "duration": self._duration
        }
        
        # Add optional parameters if they differ from defaults
        if self._precision != "normal":
            parameters["precision"] = self._precision
        
        if not self._interruptible:
            parameters["interruptible"] = self._interruptible
        
        return parameters
    
    def set_parameters(self, parameters: Dict[str, Any]):
        """Set the parameters for this step."""
        if not parameters:
            return
            
        # Set duration (always store the raw value for validation)
        duration_seconds = parameters.get("duration", 1.0)
        self._duration = duration_seconds
        
        # Convert to display units
        display_duration, display_unit = self._convert_from_seconds(duration_seconds)
        self._time_unit = display_unit
        
        # Update UI only if duration is valid for the spinbox
        if self.duration_spinbox:
            # Temporarily disconnect the signal to avoid overwriting _duration
            self.duration_spinbox.valueChanged.disconnect()
            
            # Clamp to spinbox limits for display, but keep raw value in _duration
            min_val = self.duration_spinbox.minimum()
            max_val = self.duration_spinbox.maximum()
            clamped_duration = max(min_val, min(max_val, display_duration))
            self.duration_spinbox.setValue(clamped_duration)
            
            # Reconnect the signal
            self.duration_spinbox.valueChanged.connect(self._on_duration_changed)
            
        if self.unit_combo:
            self.unit_combo.setCurrentText(display_unit)
        
        # Set optional parameters
        precision = parameters.get("precision", "normal")
        self._precision = precision
        if self.precision_combo:
            self.precision_combo.setCurrentText(precision)
        
        interruptible = parameters.get("interruptible", True)
        self._interruptible = interruptible
        if self.interruptible_checkbox:
            self.interruptible_checkbox.setChecked(interruptible)
        
        # Emit change signal
        self.emit_parameters_changed()
    
    def validate_parameters(self) -> tuple[bool, List[str]]:
        """Validate the current parameters."""
        errors = []
        
        # Always use the internal duration for validation
        # This ensures we validate the actual stored value, not the UI display
        duration_seconds = self._duration
        
        # Check duration
        if duration_seconds <= 0:
            errors.append("Duration must be greater than 0")
        elif duration_seconds > 86400:  # 24 hours in seconds
            errors.append("Duration cannot exceed 24 hours")
        elif duration_seconds < 0.001:
            errors.append("Duration cannot be less than 1 millisecond")
        
        return len(errors) == 0, errors
    
    def _on_duration_changed(self, value: float):
        """Handle duration changes."""
        # Update the internal duration in seconds
        duration_seconds = self._convert_to_seconds(value, self._time_unit)
        self._duration = duration_seconds
        self.emit_parameters_changed()
    
    def _on_unit_changed(self, text: str):
        """Handle time unit changes."""
        old_unit = self._time_unit
        self._time_unit = text
        
        # Convert the current value to the new unit
        if self.duration_spinbox:
            current_seconds = self._convert_to_seconds(self.duration_spinbox.value(), old_unit)
            new_value, _ = self._convert_from_seconds(current_seconds, text)
            self.duration_spinbox.setValue(new_value)
            
            # Update spinbox limits based on unit
            if text == "seconds":
                self.duration_spinbox.setMaximum(86400.0)  # 24 hours
                self.duration_spinbox.setDecimals(3)
            elif text == "minutes":
                self.duration_spinbox.setMaximum(1440.0)  # 24 hours
                self.duration_spinbox.setDecimals(2)
            elif text == "hours":
                self.duration_spinbox.setMaximum(24.0)  # 24 hours
                self.duration_spinbox.setDecimals(2)
        
        self.emit_parameters_changed()
    
    def _on_precision_changed(self, text: str):
        """Handle precision changes."""
        self._precision = text
        self.emit_parameters_changed()
    
    def _on_interruptible_changed(self, state: int):
        """Handle interruptible checkbox changes."""
        self._interruptible = bool(state)
        self.emit_parameters_changed()
    
    def _on_description_changed(self):
        """Handle description changes."""
        if self.description_edit:
            self._description = self.description_edit.toPlainText()
            self.emit_parameters_changed()
    
    def _set_quick_duration(self, value: float, unit: str):
        """Set duration from quick button."""
        self._time_unit = unit
        if self.unit_combo:
            self.unit_combo.setCurrentText(unit)
        if self.duration_spinbox:
            self.duration_spinbox.setValue(value)
        
        # Update the internal duration
        duration_seconds = self._convert_to_seconds(value, unit)
        self._duration = duration_seconds
        self.emit_parameters_changed()
    
    def _convert_to_seconds(self, value: float, unit: str) -> float:
        """Convert duration to seconds."""
        if unit == "minutes":
            return value * 60.0
        elif unit == "hours":
            return value * 3600.0
        else:  # seconds
            return value
    
    def _convert_from_seconds(self, seconds: float, preferred_unit: str = None) -> tuple[float, str]:
        """Convert seconds to the most appropriate unit."""
        if preferred_unit:
            if preferred_unit == "minutes":
                return seconds / 60.0, "minutes"
            elif preferred_unit == "hours":
                return seconds / 3600.0, "hours"
            else:
                return seconds, "seconds"
        
        # Auto-select best unit
        if seconds >= 3600:  # 1 hour or more
            return seconds / 3600.0, "hours"
        elif seconds >= 60:  # 1 minute or more
            return seconds / 60.0, "minutes"
        else:
            return seconds, "seconds"
    
    def get_description(self) -> str:
        """Get the step description."""
        return self._description
    
    def set_description(self, description: str):
        """Set the step description."""
        self._description = description
        if self.description_edit:
            self.description_edit.setPlainText(description)
        self.emit_parameters_changed()
    
    def get_time_unit(self) -> str:
        """Get the time unit."""
        return self._time_unit
    
    def get_precision(self) -> str:
        """Get the precision setting."""
        return self._precision
    
    def set_precision(self, precision: str):
        """Set the precision setting."""
        self._precision = precision
        if self.precision_combo:
            self.precision_combo.setCurrentText(precision)
        self.emit_parameters_changed()
    
    def get_interruptible(self) -> bool:
        """Get the interruptible setting."""
        return self._interruptible
    
    def set_interruptible(self, interruptible: bool):
        """Set the interruptible setting."""
        self._interruptible = interruptible
        if self.interruptible_checkbox:
            self.interruptible_checkbox.setChecked(interruptible)
        self.emit_parameters_changed() 