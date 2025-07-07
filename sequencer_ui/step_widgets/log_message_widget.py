"""
LogMessage Step Widget

Concrete implementation of a step widget for logging messages during sequence execution.
This widget allows users to specify log messages with different severity levels.
"""

import sys
import os
from typing import Dict, Any, List

# Add the parent directory to the path so we can import pyui
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox
from PyQt5.QtCore import Qt

try:
    from pyui.pyui.widgets.step_widget_base import StepWidgetBase
except ImportError:
    # Fallback for testing without PyUI
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import pyqtSignal
    
    class StepWidgetBase(QWidget):
        parameters_changed = pyqtSignal(dict)
        validation_changed = pyqtSignal(bool)
        
        def __init__(self, parent=None):
            super().__init__(parent)


class LogMessageWidget(StepWidgetBase):
    """
    Step widget for logging messages during sequence execution.
    
    This widget allows users to:
    - Specify a log message
    - Choose log level (info, warning, error, debug)
    - Set message category
    - Include timestamp and metadata
    """
    
    def __init__(self, parent=None):
        """Initialize the LogMessage widget."""
        super().__init__(parent)
        
        # Widget-specific attributes
        self._message = ""
        self._log_level = "info"
        self._category = "sequence"
        self._include_timestamp = True
        self._include_step_info = True
        
        # UI elements
        self.message_edit = None
        self.level_combo = None
        self.category_combo = None
        self.timestamp_checkbox = None
        self.step_info_checkbox = None
        
        # Create the UI
        self.create_ui()
        
        # Set default values
        self.set_message("Sequence step executed")
        
    def get_step_type(self) -> str:
        """Get the step type this widget represents."""
        return "LogMessage"
    
    def get_step_name(self) -> str:
        """Get the human-readable name for this step type."""
        return "Log Message"
    
    def get_step_description(self) -> str:
        """Get a description of what this step does."""
        return "Logs a message with specified severity level during sequence execution"
    
    def create_ui(self):
        """Create the UI elements for this step widget."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        
        # Message Configuration Group
        message_group = self.create_group_box("Message Configuration")
        message_layout = QVBoxLayout()
        
        # Message text
        message_label = self.create_label("Message:", bold=True)
        message_layout.addWidget(message_label)
        
        self.message_edit = self.create_text_edit(
            placeholder="Enter the message to log...",
            change_handler=self._on_message_changed
        )
        self.message_edit.setMaximumHeight(80)
        message_layout.addWidget(self.message_edit)
        
        message_group.setLayout(message_layout)
        main_layout.addWidget(message_group)
        
        # Log Configuration Group
        log_group = self.create_group_box("Log Configuration")
        log_layout = self.create_form_layout()
        
        # Log level
        self.level_combo = self.create_combo_box(
            items=["debug", "info", "warning", "error", "critical"],
            current_item="info",
            change_handler=self._on_level_changed
        )
        log_layout.addRow("Log Level:", self.level_combo)
        
        # Category
        self.category_combo = self.create_combo_box(
            items=["sequence", "system", "hardware", "software", "user", "debug"],
            current_item="sequence",
            change_handler=self._on_category_changed
        )
        log_layout.addRow("Category:", self.category_combo)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # Options Group
        options_group = self.create_group_box("Options")
        options_layout = self.create_form_layout()
        
        # Include timestamp
        self.timestamp_checkbox = self.create_checkbox(
            "Include timestamp",
            checked=True,
            change_handler=self._on_timestamp_changed
        )
        options_layout.addRow("", self.timestamp_checkbox)
        
        # Include step info
        self.step_info_checkbox = self.create_checkbox(
            "Include step information",
            checked=True,
            change_handler=self._on_step_info_changed
        )
        options_layout.addRow("", self.step_info_checkbox)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Preview Group
        preview_group = self.create_group_box("Message Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = self.create_label("", bold=False)
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 8px;
                font-family: monospace;
                color: #333333;
            }
        """)
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)
        
        # Add stretch to push content to top
        main_layout.addStretch()
        
        # Update preview initially
        self._update_preview()
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get the current parameters for this step."""
        parameters = {
            "message": self._message,
            "log_level": self._log_level
        }
        
        # Add optional parameters if they differ from defaults
        if self._category != "sequence":
            parameters["category"] = self._category
        
        if not self._include_timestamp:
            parameters["include_timestamp"] = self._include_timestamp
        
        if not self._include_step_info:
            parameters["include_step_info"] = self._include_step_info
        
        return parameters
    
    def set_parameters(self, parameters: Dict[str, Any]):
        """Set the parameters for this step."""
        if not parameters:
            return
            
        # Set message
        message = parameters.get("message", "")
        self.set_message(message)
        if self.message_edit:
            self.message_edit.setPlainText(message)
        
        # Set log level
        log_level = parameters.get("log_level", "info")
        self._log_level = log_level
        if self.level_combo:
            self.level_combo.setCurrentText(log_level)
        
        # Set optional parameters
        category = parameters.get("category", "sequence")
        self._category = category
        if self.category_combo:
            self.category_combo.setCurrentText(category)
        
        include_timestamp = parameters.get("include_timestamp", True)
        self._include_timestamp = include_timestamp
        if self.timestamp_checkbox:
            self.timestamp_checkbox.setChecked(include_timestamp)
        
        include_step_info = parameters.get("include_step_info", True)
        self._include_step_info = include_step_info
        if self.step_info_checkbox:
            self.step_info_checkbox.setChecked(include_step_info)
        
        # Update preview
        self._update_preview()
        
        # Emit change signal
        self.emit_parameters_changed()
    
    def validate_parameters(self) -> tuple[bool, List[str]]:
        """Validate the current parameters."""
        errors = []
        
        # Check message
        if not self._message.strip():
            errors.append("Log message cannot be empty")
        elif len(self._message) > 1000:
            errors.append("Log message is too long (max 1000 characters)")
        
        # Check log level
        valid_levels = ["debug", "info", "warning", "error", "critical"]
        if self._log_level not in valid_levels:
            errors.append(f"Invalid log level: {self._log_level}")
        
        return len(errors) == 0, errors
    
    def _on_message_changed(self):
        """Handle message changes."""
        if self.message_edit:
            self._message = self.message_edit.toPlainText()
            self._update_preview()
            self.emit_parameters_changed()
    
    def _on_level_changed(self, text: str):
        """Handle log level changes."""
        self._log_level = text
        self._update_preview()
        self.emit_parameters_changed()
    
    def _on_category_changed(self, text: str):
        """Handle category changes."""
        self._category = text
        self._update_preview()
        self.emit_parameters_changed()
    
    def _on_timestamp_changed(self, state: int):
        """Handle timestamp checkbox changes."""
        self._include_timestamp = bool(state)
        self._update_preview()
        self.emit_parameters_changed()
    
    def _on_step_info_changed(self, state: int):
        """Handle step info checkbox changes."""
        self._include_step_info = bool(state)
        self._update_preview()
        self.emit_parameters_changed()
    
    def _update_preview(self):
        """Update the message preview."""
        if not hasattr(self, 'preview_label') or not self.preview_label:
            return
        
        preview_parts = []
        
        # Add timestamp if enabled
        if self._include_timestamp:
            preview_parts.append("[2024-01-01 12:34:56]")
        
        # Add log level
        level_display = self._log_level.upper()
        preview_parts.append(f"[{level_display}]")
        
        # Add category
        if self._category != "sequence":
            preview_parts.append(f"[{self._category}]")
        
        # Add step info if enabled
        if self._include_step_info:
            preview_parts.append("[Step 1]")
        
        # Add message
        message = self._message or "Your message will appear here..."
        preview_parts.append(message)
        
        # Combine parts
        preview_text = " ".join(preview_parts)
        
        # Apply color based on log level
        colors = {
            "debug": "#666666",
            "info": "#000000",
            "warning": "#FF8C00",
            "error": "#CC0000",
            "critical": "#8B0000"
        }
        
        color = colors.get(self._log_level, "#000000")
        
        # Update the preview label
        self.preview_label.setText(preview_text)
        self.preview_label.setStyleSheet(f"""
            QLabel {{
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 8px;
                font-family: monospace;
                color: {color};
            }}
        """)
    
    def get_message(self) -> str:
        """Get the log message."""
        return self._message
    
    def set_message(self, message: str):
        """Set the log message."""
        self._message = message
        if self.message_edit:
            self.message_edit.setPlainText(message)
        self._update_preview()
        self.emit_parameters_changed()
    
    def get_log_level(self) -> str:
        """Get the log level."""
        return self._log_level
    
    def set_log_level(self, level: str):
        """Set the log level."""
        self._log_level = level
        if self.level_combo:
            self.level_combo.setCurrentText(level)
        self._update_preview()
        self.emit_parameters_changed()
    
    def get_category(self) -> str:
        """Get the log category."""
        return self._category
    
    def set_category(self, category: str):
        """Set the log category."""
        self._category = category
        if self.category_combo:
            self.category_combo.setCurrentText(category)
        self._update_preview()
        self.emit_parameters_changed()
    
    def get_include_timestamp(self) -> bool:
        """Get the include timestamp setting."""
        return self._include_timestamp
    
    def set_include_timestamp(self, include: bool):
        """Set the include timestamp setting."""
        self._include_timestamp = include
        if self.timestamp_checkbox:
            self.timestamp_checkbox.setChecked(include)
        self._update_preview()
        self.emit_parameters_changed()
    
    def get_include_step_info(self) -> bool:
        """Get the include step info setting."""
        return self._include_step_info
    
    def set_include_step_info(self, include: bool):
        """Set the include step info setting."""
        self._include_step_info = include
        if self.step_info_checkbox:
            self.step_info_checkbox.setChecked(include)
        self._update_preview()
        self.emit_parameters_changed() 