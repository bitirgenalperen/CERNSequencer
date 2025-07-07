"""
RunDiagnostic Step Widget

Concrete implementation of a step widget for running diagnostic tests.
This widget allows users to specify diagnostic tests to run during sequence execution.
"""

import sys
import os
from typing import Dict, Any, List

# Add the parent directory to the path so we can import pyui
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt

try:
    from pyui.pyui.widgets.step_widget_base import DiagnosticStepWidget
except ImportError:
    # Fallback for testing without PyUI
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import pyqtSignal
    
    class DiagnosticStepWidget(QWidget):
        parameters_changed = pyqtSignal(dict)
        validation_changed = pyqtSignal(bool)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self._diagnostic_name = ""
            self._diagnostic_parameters = {}


class RunDiagnosticWidget(DiagnosticStepWidget):
    """
    Step widget for running diagnostic tests.
    
    This widget allows users to:
    - Specify a diagnostic test name
    - Set diagnostic parameters
    - Choose test configuration
    - Add an optional description
    """
    
    def __init__(self, parent=None):
        """Initialize the RunDiagnostic widget."""
        super().__init__(parent)
        
        # Widget-specific attributes
        self._description = ""
        self._test_category = "system"
        self._timeout = 60.0
        self._continue_on_failure = False
        self._save_results = True
        
        # UI elements
        self.diagnostic_name_edit = None
        self.category_combo = None
        self.timeout_spinbox = None
        self.continue_checkbox = None
        self.save_results_checkbox = None
        self.parameters_table = None
        self.description_edit = None
        
        # Create the UI
        self.create_ui()
        
        # Set default values
        self.set_diagnostic_name("System_Health_Check")
        
    def get_step_type(self) -> str:
        """Get the step type this widget represents."""
        return "RunDiagnostic"
    
    def get_step_name(self) -> str:
        """Get the human-readable name for this step type."""
        return "Run Diagnostic"
    
    def get_step_description(self) -> str:
        """Get a description of what this step does."""
        return "Runs a diagnostic test or health check on accelerator components"
    
    def create_ui(self):
        """Create the UI elements for this step widget."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        
        # Diagnostic Configuration Group
        diag_group = self.create_group_box("Diagnostic Configuration")
        diag_layout = self.create_form_layout()
        
        # Diagnostic name
        self.diagnostic_name_edit = self.create_line_edit(
            placeholder="e.g., System_Health_Check, Magnet_Test, RF_Calibration",
            change_handler=self._on_diagnostic_name_changed
        )
        diag_layout.addRow("Diagnostic Name:", self.diagnostic_name_edit)
        
        # Test category
        self.category_combo = self.create_combo_box(
            items=["system", "hardware", "software", "calibration", "safety", "performance"],
            current_item="system",
            change_handler=self._on_category_changed
        )
        diag_layout.addRow("Test Category:", self.category_combo)
        
        # Timeout
        self.timeout_spinbox = self.create_double_spin_box(
            minimum=1.0,
            maximum=3600.0,  # Max 1 hour
            value=60.0,
            decimals=1,
            change_handler=self._on_timeout_changed
        )
        self.timeout_spinbox.setSuffix(" seconds")
        diag_layout.addRow("Timeout:", self.timeout_spinbox)
        
        diag_group.setLayout(diag_layout)
        main_layout.addWidget(diag_group)
        
        # Test Parameters Group
        params_group = self.create_group_box("Test Parameters")
        params_layout = QVBoxLayout()
        
        # Parameters table
        self.parameters_table = QTableWidget(0, 2)
        self.parameters_table.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.parameters_table.horizontalHeader().setStretchLastSection(True)
        self.parameters_table.setMaximumHeight(150)
        params_layout.addWidget(self.parameters_table)
        
        # Parameter buttons
        param_buttons_layout = QHBoxLayout()
        
        add_param_btn = QPushButton("Add Parameter")
        add_param_btn.clicked.connect(self._add_parameter)
        param_buttons_layout.addWidget(add_param_btn)
        
        remove_param_btn = QPushButton("Remove Parameter")
        remove_param_btn.clicked.connect(self._remove_parameter)
        param_buttons_layout.addWidget(remove_param_btn)
        
        param_buttons_layout.addStretch()
        params_layout.addLayout(param_buttons_layout)
        
        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)
        
        # Options Group
        options_group = self.create_group_box("Options")
        options_layout = self.create_form_layout()
        
        # Continue on failure
        self.continue_checkbox = self.create_checkbox(
            "Continue sequence on test failure",
            checked=False,
            change_handler=self._on_continue_changed
        )
        options_layout.addRow("", self.continue_checkbox)
        
        # Save results
        self.save_results_checkbox = self.create_checkbox(
            "Save test results",
            checked=True,
            change_handler=self._on_save_results_changed
        )
        options_layout.addRow("", self.save_results_checkbox)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Description Group
        desc_group = self.create_group_box("Description")
        desc_layout = QVBoxLayout()
        
        self.description_edit = self.create_text_edit(
            placeholder="Optional description of what this diagnostic test does...",
            change_handler=self._on_description_changed
        )
        desc_layout.addWidget(self.description_edit)
        
        desc_group.setLayout(desc_layout)
        main_layout.addWidget(desc_group)
        
        # Add stretch to push content to top
        main_layout.addStretch()
        
        # Add some default parameters
        self._add_default_parameters()
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get the current parameters for this step."""
        parameters = {
            "diagnostic_name": self.get_diagnostic_name(),
            "test_parameters": self.get_diagnostic_parameters()
        }
        
        # Add optional parameters if they differ from defaults
        if self._test_category != "system":
            parameters["test_category"] = self._test_category
        
        if self._timeout != 60.0:
            parameters["timeout"] = self._timeout
        
        if self._continue_on_failure:
            parameters["continue_on_failure"] = self._continue_on_failure
        
        if not self._save_results:
            parameters["save_results"] = self._save_results
        
        return parameters
    
    def set_parameters(self, parameters: Dict[str, Any]):
        """Set the parameters for this step."""
        if not parameters:
            return
            
        # Set diagnostic name
        diagnostic_name = parameters.get("diagnostic_name", "")
        self.set_diagnostic_name(diagnostic_name)
        if self.diagnostic_name_edit:
            self.diagnostic_name_edit.setText(diagnostic_name)
        
        # Set test parameters
        test_params = parameters.get("test_parameters", {})
        self.set_diagnostic_parameters(test_params)
        self._update_parameters_table()
        
        # Set optional parameters
        test_category = parameters.get("test_category", "system")
        self._test_category = test_category
        if self.category_combo:
            self.category_combo.setCurrentText(test_category)
        
        timeout = parameters.get("timeout", 60.0)
        self._timeout = timeout
        if self.timeout_spinbox:
            self.timeout_spinbox.setValue(timeout)
        
        continue_on_failure = parameters.get("continue_on_failure", False)
        self._continue_on_failure = continue_on_failure
        if self.continue_checkbox:
            self.continue_checkbox.setChecked(continue_on_failure)
        
        save_results = parameters.get("save_results", True)
        self._save_results = save_results
        if self.save_results_checkbox:
            self.save_results_checkbox.setChecked(save_results)
        
        # Emit change signal
        self.emit_parameters_changed()
    
    def validate_parameters(self) -> tuple[bool, List[str]]:
        """Validate the current parameters."""
        errors = []
        
        # Check diagnostic name
        if not self.get_diagnostic_name().strip():
            errors.append("Diagnostic name is required")
        elif not self._is_valid_diagnostic_name(self.get_diagnostic_name()):
            errors.append("Diagnostic name contains invalid characters")
        
        # Check timeout
        if self._timeout <= 0:
            errors.append("Timeout must be greater than 0")
        elif self._timeout > 3600:
            errors.append("Timeout cannot exceed 1 hour")
        
        # Check parameters
        params = self.get_diagnostic_parameters()
        for param_name, param_value in params.items():
            if not param_name.strip():
                errors.append("Parameter names cannot be empty")
                break
        
        return len(errors) == 0, errors
    
    def _on_diagnostic_name_changed(self, text: str):
        """Handle diagnostic name changes."""
        self.set_diagnostic_name(text)
    
    def _on_category_changed(self, text: str):
        """Handle category changes."""
        self._test_category = text
        self.emit_parameters_changed()
    
    def _on_timeout_changed(self, value: float):
        """Handle timeout changes."""
        self._timeout = value
        self.emit_parameters_changed()
    
    def _on_continue_changed(self, state: int):
        """Handle continue on failure checkbox changes."""
        self._continue_on_failure = bool(state)
        self.emit_parameters_changed()
    
    def _on_save_results_changed(self, state: int):
        """Handle save results checkbox changes."""
        self._save_results = bool(state)
        self.emit_parameters_changed()
    
    def _on_description_changed(self):
        """Handle description changes."""
        if self.description_edit:
            self._description = self.description_edit.toPlainText()
            self.emit_parameters_changed()
    
    def _add_parameter(self):
        """Add a new parameter row to the table."""
        row = self.parameters_table.rowCount()
        self.parameters_table.insertRow(row)
        
        # Add default items
        self.parameters_table.setItem(row, 0, QTableWidgetItem("parameter_name"))
        self.parameters_table.setItem(row, 1, QTableWidgetItem("value"))
        
        # Connect to change handler
        self.parameters_table.itemChanged.connect(self._on_parameter_changed)
        
        self.emit_parameters_changed()
    
    def _remove_parameter(self):
        """Remove the selected parameter row from the table."""
        current_row = self.parameters_table.currentRow()
        if current_row >= 0:
            self.parameters_table.removeRow(current_row)
            self.emit_parameters_changed()
    
    def _on_parameter_changed(self, item):
        """Handle parameter table changes."""
        # Update the internal parameters dict
        params = {}
        for row in range(self.parameters_table.rowCount()):
            name_item = self.parameters_table.item(row, 0)
            value_item = self.parameters_table.item(row, 1)
            
            if name_item and value_item:
                name = name_item.text().strip()
                value = value_item.text().strip()
                if name:  # Only add non-empty names
                    params[name] = value
        
        self.set_diagnostic_parameters(params)
    
    def _update_parameters_table(self):
        """Update the parameters table with current parameters."""
        # Clear existing rows
        self.parameters_table.setRowCount(0)
        
        # Add parameters
        params = self.get_diagnostic_parameters()
        for param_name, param_value in params.items():
            row = self.parameters_table.rowCount()
            self.parameters_table.insertRow(row)
            self.parameters_table.setItem(row, 0, QTableWidgetItem(param_name))
            self.parameters_table.setItem(row, 1, QTableWidgetItem(str(param_value)))
        
        # Connect to change handler
        self.parameters_table.itemChanged.connect(self._on_parameter_changed)
    
    def _add_default_parameters(self):
        """Add some default parameters based on category."""
        default_params = {
            "verbose": "true",
            "timeout_action": "abort"
        }
        
        self.set_diagnostic_parameters(default_params)
        self._update_parameters_table()
    
    def _is_valid_diagnostic_name(self, name: str) -> bool:
        """Check if diagnostic name is valid."""
        if not name.strip():
            return False
        
        # Basic validation: alphanumeric, underscore, dash
        import re
        return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name.strip()))
    
    def get_description(self) -> str:
        """Get the step description."""
        return self._description
    
    def set_description(self, description: str):
        """Set the step description."""
        self._description = description
        if self.description_edit:
            self.description_edit.setPlainText(description)
        self.emit_parameters_changed()
    
    def get_test_category(self) -> str:
        """Get the test category."""
        return self._test_category
    
    def set_test_category(self, category: str):
        """Set the test category."""
        self._test_category = category
        if self.category_combo:
            self.category_combo.setCurrentText(category)
        self.emit_parameters_changed()
    
    def get_timeout(self) -> float:
        """Get the timeout value."""
        return self._timeout
    
    def set_timeout(self, timeout: float):
        """Set the timeout value."""
        self._timeout = timeout
        if self.timeout_spinbox:
            self.timeout_spinbox.setValue(timeout)
        self.emit_parameters_changed()
    
    def get_continue_on_failure(self) -> bool:
        """Get the continue on failure setting."""
        return self._continue_on_failure
    
    def set_continue_on_failure(self, continue_on_failure: bool):
        """Set the continue on failure setting."""
        self._continue_on_failure = continue_on_failure
        if self.continue_checkbox:
            self.continue_checkbox.setChecked(continue_on_failure)
        self.emit_parameters_changed()
    
    def get_save_results(self) -> bool:
        """Get the save results setting."""
        return self._save_results
    
    def set_save_results(self, save_results: bool):
        """Set the save results setting."""
        self._save_results = save_results
        if self.save_results_checkbox:
            self.save_results_checkbox.setChecked(save_results)
        self.emit_parameters_changed() 