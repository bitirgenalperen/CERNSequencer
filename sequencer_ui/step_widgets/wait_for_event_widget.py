"""
WaitForEvent Step Widget

Concrete implementation of a step widget for waiting for accelerator events.
This widget allows users to specify an event name and timeout for waiting
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
    from pyui.pyui.widgets.step_widget_base import EventStepWidget
except ImportError:
    # Fallback for testing without PyUI
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import pyqtSignal
    
    class EventStepWidget(QWidget):
        parameters_changed = pyqtSignal(dict)
        validation_changed = pyqtSignal(bool)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self._event_name = ""
            self._event_timeout = 30.0


class WaitForEventWidget(EventStepWidget):
    """
    Step widget for waiting for accelerator events.
    
    This widget allows users to:
    - Specify an event name to wait for
    - Set a timeout for the wait operation
    - Choose event matching criteria
    - Add an optional description
    """
    
    def __init__(self, parent=None):
        """Initialize the WaitForEvent widget."""
        super().__init__(parent)
        
        # Widget-specific attributes
        self._description = ""
        self._event_source = "any"
        self._match_criteria = "exact"
        self._retry_on_timeout = False
        
        # UI elements
        self.event_name_edit = None
        self.timeout_spinbox = None
        self.source_combo = None
        self.criteria_combo = None
        self.retry_checkbox = None
        self.description_edit = None
        
        # Create the UI
        self.create_ui()
        
        # Set default values
        self.set_event_timeout(30.0)  # Default 30 second timeout
        
    def get_step_type(self) -> str:
        """Get the step type this widget represents."""
        return "WaitForEvent"
    
    def get_step_name(self) -> str:
        """Get the human-readable name for this step type."""
        return "Wait for Event"
    
    def get_step_description(self) -> str:
        """Get a description of what this step does."""
        return "Waits for a specified event to occur in the accelerator control system"
    
    def create_ui(self):
        """Create the UI elements for this step widget."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        
        # Event Configuration Group
        event_group = self.create_group_box("Event Configuration")
        event_layout = self.create_form_layout()
        
        # Event name
        self.event_name_edit = self.create_line_edit(
            placeholder="e.g., Beam_Ready, Magnet_Stable, RF_On",
            change_handler=self._on_event_name_changed
        )
        event_layout.addRow("Event Name:", self.event_name_edit)
        
        # Event source
        self.source_combo = self.create_combo_box(
            items=["any", "control_system", "hardware", "software", "user"],
            current_item="any",
            change_handler=self._on_source_changed
        )
        event_layout.addRow("Event Source:", self.source_combo)
        
        # Match criteria
        self.criteria_combo = self.create_combo_box(
            items=["exact", "contains", "starts_with", "ends_with"],
            current_item="exact",
            change_handler=self._on_criteria_changed
        )
        event_layout.addRow("Match Criteria:", self.criteria_combo)
        
        event_group.setLayout(event_layout)
        main_layout.addWidget(event_group)
        
        # Timeout Configuration Group
        timeout_group = self.create_group_box("Timeout Configuration")
        timeout_layout = self.create_form_layout()
        
        # Timeout value
        self.timeout_spinbox = self.create_double_spin_box(
            minimum=0.1,
            maximum=3600.0,  # Max 1 hour
            value=30.0,
            decimals=1,
            change_handler=self._on_timeout_changed
        )
        self.timeout_spinbox.setSuffix(" seconds")
        timeout_layout.addRow("Timeout:", self.timeout_spinbox)
        
        # Retry on timeout
        self.retry_checkbox = self.create_checkbox(
            "Retry on timeout",
            checked=False,
            change_handler=self._on_retry_changed
        )
        timeout_layout.addRow("", self.retry_checkbox)
        
        timeout_group.setLayout(timeout_layout)
        main_layout.addWidget(timeout_group)
        
        # Description Group
        desc_group = self.create_group_box("Description")
        desc_layout = QVBoxLayout()
        
        self.description_edit = self.create_text_edit(
            placeholder="Optional description of what event you're waiting for...",
            change_handler=self._on_description_changed
        )
        desc_layout.addWidget(self.description_edit)
        
        desc_group.setLayout(desc_layout)
        main_layout.addWidget(desc_group)
        
        # Add stretch to push content to top
        main_layout.addStretch()
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get the current parameters for this step."""
        parameters = {
            "event_name": self.get_event_name(),
            "timeout": self.get_event_timeout()
        }
        
        # Add optional parameters if they differ from defaults
        if self._event_source != "any":
            parameters["event_source"] = self._event_source
        
        if self._match_criteria != "exact":
            parameters["match_criteria"] = self._match_criteria
        
        if self._retry_on_timeout:
            parameters["retry_on_timeout"] = self._retry_on_timeout
        
        return parameters
    
    def set_parameters(self, parameters: Dict[str, Any]):
        """Set the parameters for this step."""
        if not parameters:
            return
            
        # Set event name
        event_name = parameters.get("event_name", "")
        self.set_event_name(event_name)
        if self.event_name_edit:
            self.event_name_edit.setText(event_name)
        
        # Set timeout
        timeout = parameters.get("timeout", 30.0)
        self.set_event_timeout(timeout)
        if self.timeout_spinbox:
            self.timeout_spinbox.setValue(timeout)
        
        # Set optional parameters
        event_source = parameters.get("event_source", "any")
        self._event_source = event_source
        if self.source_combo:
            self.source_combo.setCurrentText(event_source)
        
        match_criteria = parameters.get("match_criteria", "exact")
        self._match_criteria = match_criteria
        if self.criteria_combo:
            self.criteria_combo.setCurrentText(match_criteria)
        
        retry_on_timeout = parameters.get("retry_on_timeout", False)
        self._retry_on_timeout = retry_on_timeout
        if self.retry_checkbox:
            self.retry_checkbox.setChecked(retry_on_timeout)
        
        # Emit change signal
        self.emit_parameters_changed()
    
    def validate_parameters(self) -> tuple[bool, List[str]]:
        """Validate the current parameters."""
        errors = []
        
        # Check event name
        if not self.get_event_name().strip():
            errors.append("Event name is required")
        elif not self._is_valid_event_name(self.get_event_name()):
            errors.append("Event name contains invalid characters")
        
        # Check timeout
        timeout = self.get_event_timeout()
        if timeout <= 0:
            errors.append("Timeout must be greater than 0")
        elif timeout > 3600:
            errors.append("Timeout cannot exceed 1 hour (3600 seconds)")
        
        return len(errors) == 0, errors
    
    def _on_event_name_changed(self, text: str):
        """Handle event name changes."""
        self.set_event_name(text)
    
    def _on_timeout_changed(self, value: float):
        """Handle timeout changes."""
        self.set_event_timeout(value)
    
    def _on_source_changed(self, text: str):
        """Handle event source changes."""
        self._event_source = text
        self.emit_parameters_changed()
    
    def _on_criteria_changed(self, text: str):
        """Handle match criteria changes."""
        self._match_criteria = text
        self.emit_parameters_changed()
    
    def _on_retry_changed(self, state: int):
        """Handle retry checkbox changes."""
        self._retry_on_timeout = bool(state)
        self.emit_parameters_changed()
    
    def _on_description_changed(self):
        """Handle description changes."""
        if self.description_edit:
            self._description = self.description_edit.toPlainText()
            self.emit_parameters_changed()
    
    def _is_valid_event_name(self, name: str) -> bool:
        """Check if event name is valid."""
        if not name.strip():
            return False
        
        # Basic validation: alphanumeric, underscore, dash, dot
        import re
        return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_.-]*$', name.strip()))
    
    def get_description(self) -> str:
        """Get the step description."""
        return self._description
    
    def set_description(self, description: str):
        """Set the step description."""
        self._description = description
        if self.description_edit:
            self.description_edit.setPlainText(description)
        self.emit_parameters_changed()
    
    def get_event_source(self) -> str:
        """Get the event source."""
        return self._event_source
    
    def set_event_source(self, source: str):
        """Set the event source."""
        self._event_source = source
        if self.source_combo:
            self.source_combo.setCurrentText(source)
        self.emit_parameters_changed()
    
    def get_match_criteria(self) -> str:
        """Get the match criteria."""
        return self._match_criteria
    
    def set_match_criteria(self, criteria: str):
        """Set the match criteria."""
        self._match_criteria = criteria
        if self.criteria_combo:
            self.criteria_combo.setCurrentText(criteria)
        self.emit_parameters_changed()
    
    def get_retry_on_timeout(self) -> bool:
        """Get the retry on timeout setting."""
        return self._retry_on_timeout
    
    def set_retry_on_timeout(self, retry: bool):
        """Set the retry on timeout setting."""
        self._retry_on_timeout = retry
        if self.retry_checkbox:
            self.retry_checkbox.setChecked(retry)
        self.emit_parameters_changed() 