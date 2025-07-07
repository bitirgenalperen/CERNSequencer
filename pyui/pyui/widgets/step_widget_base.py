"""
Step Widget Base Classes

Abstract base classes and interfaces for sequence step widgets in PyUI.
These classes provide the foundation for creating step widgets that can be
used in sequence editors and other PyUI applications.
"""

from abc import abstractmethod
from typing import Dict, Any, Optional, List
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
                             QCheckBox, QTextEdit, QGroupBox, QFormLayout)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont


class StepWidgetBase(QWidget):
    """
    Abstract base class for all step widgets.
    
    This class defines the interface that all step widgets must implement
    to be compatible with the PyUI sequence editor system.
    """
    
    # Signals
    parameters_changed = pyqtSignal(dict)  # Emitted when parameters change
    validation_changed = pyqtSignal(bool)  # Emitted when validation status changes
    
    def __init__(self, parent=None):
        """Initialize the step widget base.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._parameters = {}
        self._is_valid = True
        self._validation_errors = []
        self._setup_base_ui()
        
    def _setup_base_ui(self):
        """Set up the base UI structure."""
        self.setObjectName("StepWidget")
        self.setStyleSheet("""
            QWidget#StepWidget {
                background-color: #F8F8F8;
                border: 1px solid #CCCCCC;
                border-radius: 6px;
                margin: 2px;
            }
            QGroupBox {
                font-weight: bold;
                color: #0066CC;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                margin-top: 6px;
                padding-top: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px;
                background-color: white;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, 
            QComboBox:focus, QTextEdit:focus {
                border-color: #0066CC;
            }
            QCheckBox {
                color: #333333;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #CCCCCC;
                background-color: white;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #0066CC;
                background-color: #0066CC;
                border-radius: 2px;
            }
        """)
        
    @abstractmethod
    def get_step_type(self) -> str:
        """Get the step type this widget represents.
        
        Returns:
            str: The step type name (e.g., "SetParameter", "Delay")
        """
        pass
    
    @abstractmethod
    def get_step_name(self) -> str:
        """Get the human-readable name for this step type.
        
        Returns:
            str: Human-readable step name
        """
        pass
    
    @abstractmethod
    def get_step_description(self) -> str:
        """Get a description of what this step does.
        
        Returns:
            str: Step description
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get the current parameters for this step.
        
        Returns:
            Dict[str, Any]: Current parameter values
        """
        pass
    
    @abstractmethod
    def set_parameters(self, parameters: Dict[str, Any]):
        """Set the parameters for this step.
        
        Args:
            parameters: Dictionary of parameter values
        """
        pass
    
    @abstractmethod
    def validate_parameters(self) -> tuple[bool, List[str]]:
        """Validate the current parameters.
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        pass
    
    @abstractmethod
    def create_ui(self):
        """Create the UI elements for this step widget.
        
        This method should be implemented by subclasses to create
        the specific UI for their step type.
        """
        pass
    
    def get_validation_errors(self) -> List[str]:
        """Get the current validation errors.
        
        Returns:
            List[str]: List of validation error messages
        """
        return self._validation_errors.copy()
    
    def is_valid(self) -> bool:
        """Check if the current parameters are valid.
        
        Returns:
            bool: True if parameters are valid
        """
        return self._is_valid
    
    def refresh_validation(self):
        """Refresh the validation status and emit signals if changed."""
        old_valid = self._is_valid
        self._is_valid, self._validation_errors = self.validate_parameters()
        
        if old_valid != self._is_valid:
            self.validation_changed.emit(self._is_valid)
    
    def emit_parameters_changed(self):
        """Emit the parameters_changed signal with current parameters."""
        self._parameters = self.get_parameters()
        self.parameters_changed.emit(self._parameters)
        self.refresh_validation()
    
    def create_form_layout(self) -> QFormLayout:
        """Create a standard form layout for parameter input.
        
        Returns:
            QFormLayout: Form layout for parameters
        """
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form_layout.setSpacing(8)
        return form_layout
    
    def create_group_box(self, title: str) -> QGroupBox:
        """Create a styled group box.
        
        Args:
            title: Group box title
            
        Returns:
            QGroupBox: Styled group box
        """
        group_box = QGroupBox(title)
        return group_box
    
    def create_label(self, text: str, bold: bool = False) -> QLabel:
        """Create a styled label.
        
        Args:
            text: Label text
            bold: Whether to make the text bold
            
        Returns:
            QLabel: Styled label
        """
        label = QLabel(text)
        if bold:
            font = QFont()
            font.setBold(True)
            label.setFont(font)
        return label
    
    def create_line_edit(self, placeholder: str = "", 
                        change_handler=None) -> QLineEdit:
        """Create a styled line edit.
        
        Args:
            placeholder: Placeholder text
            change_handler: Optional change handler function
            
        Returns:
            QLineEdit: Styled line edit
        """
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        if change_handler:
            line_edit.textChanged.connect(change_handler)
        return line_edit
    
    def create_spin_box(self, minimum: int = 0, maximum: int = 100,
                       value: int = 0, change_handler=None) -> QSpinBox:
        """Create a styled spin box.
        
        Args:
            minimum: Minimum value
            maximum: Maximum value
            value: Initial value
            change_handler: Optional change handler function
            
        Returns:
            QSpinBox: Styled spin box
        """
        spin_box = QSpinBox()
        spin_box.setMinimum(minimum)
        spin_box.setMaximum(maximum)
        spin_box.setValue(value)
        if change_handler:
            spin_box.valueChanged.connect(change_handler)
        return spin_box
    
    def create_double_spin_box(self, minimum: float = 0.0, maximum: float = 100.0,
                              value: float = 0.0, decimals: int = 2,
                              change_handler=None) -> QDoubleSpinBox:
        """Create a styled double spin box.
        
        Args:
            minimum: Minimum value
            maximum: Maximum value
            value: Initial value
            decimals: Number of decimal places
            change_handler: Optional change handler function
            
        Returns:
            QDoubleSpinBox: Styled double spin box
        """
        double_spin_box = QDoubleSpinBox()
        double_spin_box.setMinimum(minimum)
        double_spin_box.setMaximum(maximum)
        double_spin_box.setValue(value)
        double_spin_box.setDecimals(decimals)
        if change_handler:
            double_spin_box.valueChanged.connect(change_handler)
        return double_spin_box
    
    def create_combo_box(self, items: List[str], current_item: str = "",
                        change_handler=None) -> QComboBox:
        """Create a styled combo box.
        
        Args:
            items: List of items for the combo box
            current_item: Currently selected item
            change_handler: Optional change handler function
            
        Returns:
            QComboBox: Styled combo box
        """
        combo_box = QComboBox()
        combo_box.addItems(items)
        if current_item and current_item in items:
            combo_box.setCurrentText(current_item)
        if change_handler:
            combo_box.currentTextChanged.connect(change_handler)
        return combo_box
    
    def create_checkbox(self, text: str, checked: bool = False,
                       change_handler=None) -> QCheckBox:
        """Create a styled checkbox.
        
        Args:
            text: Checkbox text
            checked: Initial checked state
            change_handler: Optional change handler function
            
        Returns:
            QCheckBox: Styled checkbox
        """
        checkbox = QCheckBox(text)
        checkbox.setChecked(checked)
        if change_handler:
            checkbox.stateChanged.connect(change_handler)
        return checkbox
    
    def create_text_edit(self, placeholder: str = "", 
                        change_handler=None) -> QTextEdit:
        """Create a styled text edit.
        
        Args:
            placeholder: Placeholder text
            change_handler: Optional change handler function
            
        Returns:
            QTextEdit: Styled text edit
        """
        text_edit = QTextEdit()
        text_edit.setPlaceholderText(placeholder)
        text_edit.setMaximumHeight(100)  # Reasonable height for most uses
        if change_handler:
            text_edit.textChanged.connect(change_handler)
        return text_edit


class ParameterStepWidget(StepWidgetBase):
    """
    Base class for step widgets that deal with parameter manipulation.
    
    This class provides common functionality for steps that set, get, or
    manipulate parameters in the accelerator control system.
    """
    
    def __init__(self, parent=None):
        """Initialize the parameter step widget."""
        super().__init__(parent)
        self._parameter_name = ""
        self._parameter_value = None
        self._parameter_type = "string"
        
    def get_parameter_name(self) -> str:
        """Get the parameter name.
        
        Returns:
            str: Parameter name
        """
        return self._parameter_name
    
    def set_parameter_name(self, name: str):
        """Set the parameter name.
        
        Args:
            name: Parameter name
        """
        self._parameter_name = name
        self.emit_parameters_changed()
    
    def get_parameter_value(self) -> Any:
        """Get the parameter value.
        
        Returns:
            Any: Parameter value
        """
        return self._parameter_value
    
    def set_parameter_value(self, value: Any):
        """Set the parameter value.
        
        Args:
            value: Parameter value
        """
        self._parameter_value = value
        self.emit_parameters_changed()
    
    def get_parameter_type(self) -> str:
        """Get the parameter type.
        
        Returns:
            str: Parameter type (string, number, boolean)
        """
        return self._parameter_type
    
    def set_parameter_type(self, param_type: str):
        """Set the parameter type.
        
        Args:
            param_type: Parameter type
        """
        self._parameter_type = param_type
        self.emit_parameters_changed()


class TimingStepWidget(StepWidgetBase):
    """
    Base class for step widgets that deal with timing operations.
    
    This class provides common functionality for steps that involve
    delays, timeouts, or other timing-related operations.
    """
    
    def __init__(self, parent=None):
        """Initialize the timing step widget."""
        super().__init__(parent)
        self._duration = 0.0
        self._timeout = None
        
    def get_duration(self) -> float:
        """Get the duration value.
        
        Returns:
            float: Duration in seconds
        """
        return self._duration
    
    def set_duration(self, duration: float):
        """Set the duration value.
        
        Args:
            duration: Duration in seconds
        """
        self._duration = max(0.0, duration)  # Ensure non-negative
        self.emit_parameters_changed()
    
    def get_timeout(self) -> Optional[float]:
        """Get the timeout value.
        
        Returns:
            Optional[float]: Timeout in seconds, or None if no timeout
        """
        return self._timeout
    
    def set_timeout(self, timeout: Optional[float]):
        """Set the timeout value.
        
        Args:
            timeout: Timeout in seconds, or None for no timeout
        """
        self._timeout = timeout if timeout is None else max(0.0, timeout)
        self.emit_parameters_changed()


class EventStepWidget(StepWidgetBase):
    """
    Base class for step widgets that deal with event operations.
    
    This class provides common functionality for steps that wait for
    events, trigger events, or monitor event states.
    """
    
    def __init__(self, parent=None):
        """Initialize the event step widget."""
        super().__init__(parent)
        self._event_name = ""
        self._event_timeout = 30.0
        
    def get_event_name(self) -> str:
        """Get the event name.
        
        Returns:
            str: Event name
        """
        return self._event_name
    
    def set_event_name(self, name: str):
        """Set the event name.
        
        Args:
            name: Event name
        """
        self._event_name = name
        self.emit_parameters_changed()
    
    def get_event_timeout(self) -> float:
        """Get the event timeout.
        
        Returns:
            float: Event timeout in seconds
        """
        return self._event_timeout
    
    def set_event_timeout(self, timeout: float):
        """Set the event timeout.
        
        Args:
            timeout: Event timeout in seconds
        """
        self._event_timeout = max(0.0, timeout)
        self.emit_parameters_changed()


class DiagnosticStepWidget(StepWidgetBase):
    """
    Base class for step widgets that deal with diagnostic operations.
    
    This class provides common functionality for steps that run
    diagnostics, tests, or health checks on accelerator components.
    """
    
    def __init__(self, parent=None):
        """Initialize the diagnostic step widget."""
        super().__init__(parent)
        self._diagnostic_name = ""
        self._diagnostic_parameters = {}
        
    def get_diagnostic_name(self) -> str:
        """Get the diagnostic name.
        
        Returns:
            str: Diagnostic name
        """
        return self._diagnostic_name
    
    def set_diagnostic_name(self, name: str):
        """Set the diagnostic name.
        
        Args:
            name: Diagnostic name
        """
        self._diagnostic_name = name
        self.emit_parameters_changed()
    
    def get_diagnostic_parameters(self) -> Dict[str, Any]:
        """Get the diagnostic parameters.
        
        Returns:
            Dict[str, Any]: Diagnostic parameters
        """
        return self._diagnostic_parameters.copy()
    
    def set_diagnostic_parameters(self, parameters: Dict[str, Any]):
        """Set the diagnostic parameters.
        
        Args:
            parameters: Diagnostic parameters
        """
        self._diagnostic_parameters = parameters.copy()
        self.emit_parameters_changed()
    
    def add_diagnostic_parameter(self, name: str, value: Any):
        """Add a diagnostic parameter.
        
        Args:
            name: Parameter name
            value: Parameter value
        """
        self._diagnostic_parameters[name] = value
        self.emit_parameters_changed()
    
    def remove_diagnostic_parameter(self, name: str):
        """Remove a diagnostic parameter.
        
        Args:
            name: Parameter name to remove
        """
        if name in self._diagnostic_parameters:
            del self._diagnostic_parameters[name]
            self.emit_parameters_changed() 