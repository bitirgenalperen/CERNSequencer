"""
Sequence Editor Module

This module contains the UI logic for editing sequences within the Sequencer UI.
The SequenceEditor is responsible for:
- Displaying sequence steps in an editable format
- Managing the in-memory sequence data structure
- Providing UI for adding, removing, and reordering steps
- Integrating with step widgets for parameter configuration
"""

import sys
import os
from typing import Dict, Any, List, Optional

# Add the parent directory to the path so we can import pyui
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                             QFrame, QLabel, QPushButton, QSplitter, QGroupBox,
                             QListWidget, QListWidgetItem, QStackedWidget,
                             QComboBox, QMessageBox, QMenu, QAction)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData
from PyQt5.QtGui import QDrag, QPixmap, QPainter

from pyui.pyui import get_widget
from .sequence_data_model import SequenceData, SequenceStep, StepType, create_example_sequence
from .step_widgets import get_step_widget_class, get_available_step_types, create_step_widget


class StepListItem(QListWidgetItem):
    """Custom list item for sequence steps with drag/drop support."""
    
    def __init__(self, step: SequenceStep, parent=None):
        super().__init__(parent)
        self.step = step
        self.update_display()
        
    def update_display(self):
        """Update the display text for this step."""
        step_name = self.step.step_type.value
        description = self.step.description[:50] + "..." if len(self.step.description) > 50 else self.step.description
        
        if description:
            display_text = f"{step_name}: {description}"
        else:
            # Show key parameter info if no description
            if self.step.step_type == StepType.SET_PARAMETER:
                param_name = self.step.parameters.get('name', 'Unknown')
                param_value = self.step.parameters.get('value', 'Unknown')
                display_text = f"{step_name}: {param_name} = {param_value}"
            elif self.step.step_type == StepType.WAIT_FOR_EVENT:
                event_name = self.step.parameters.get('event_name', 'Unknown')
                display_text = f"{step_name}: {event_name}"
            elif self.step.step_type == StepType.DELAY:
                duration = self.step.parameters.get('duration', 0)
                display_text = f"{step_name}: {duration}s"
            elif self.step.step_type == StepType.RUN_DIAGNOSTIC:
                diagnostic_name = self.step.parameters.get('diagnostic_name', 'Unknown')
                display_text = f"{step_name}: {diagnostic_name}"
            elif self.step.step_type == StepType.LOG_MESSAGE:
                message = self.step.parameters.get('message', 'Unknown')[:30]
                display_text = f"{step_name}: {message}"
            else:
                display_text = step_name
        
        self.setText(display_text)
        
        # Set tooltip with full information
        tooltip = f"Step Type: {step_name}\n"
        tooltip += f"ID: {self.step.step_id}\n"
        tooltip += f"Enabled: {'Yes' if self.step.enabled else 'No'}\n"
        if self.step.description:
            tooltip += f"Description: {self.step.description}\n"
        tooltip += f"Parameters: {self.step.parameters}"
        self.setToolTip(tooltip)


class StepListWidget(QListWidget):
    """Custom list widget with drag/drop support for reordering steps."""
    
    steps_reordered = pyqtSignal(int, int)  # old_index, new_index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        
    def dropEvent(self, event):
        """Handle drop events for reordering."""
        if event.source() == self:
            old_index = self.currentRow()
            super().dropEvent(event)
            new_index = self.currentRow()
            
            if old_index != new_index and old_index >= 0 and new_index >= 0:
                self.steps_reordered.emit(old_index, new_index)


class SequenceEditor(QWidget):
    """
    Main sequence editor widget for managing operational sequences.
    
    This widget provides functionality for:
    - Creating, loading, and managing sequences
    - Adding, removing, and reordering sequence steps
    - Editing step parameters using appropriate step widgets
    - Validating sequence data
    """
    
    # Signals
    sequence_changed = pyqtSignal()  # Emitted when sequence data changes
    sequence_loaded = pyqtSignal(str)  # Emitted when sequence is loaded (sequence name)
    step_selected = pyqtSignal(str)  # Emitted when step is selected (step ID)
    
    def __init__(self, parent=None):
        """
        Initialize the sequence editor.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        # Current sequence data
        self._sequence_data = None
        self._current_step_id = None
        self._is_modified = False
        
        # UI components
        self.step_list = None
        self.step_widget_stack = None
        self.add_step_combo = None
        self.sequence_info_label = None
        self.step_widgets = {}  # step_id -> widget mapping
        
        # Setup UI
        self.setup_ui()
        
        # Load empty sequence by default
        self.new_sequence()
        
    def setup_ui(self):
        """Set up the sequence editor UI."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Sequence info header
        self.sequence_info_label = QLabel("No sequence loaded")
        self.sequence_info_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #0066CC;
                padding: 8px;
                background-color: #F0F8FF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
            }
        """)
        main_layout.addWidget(self.sequence_info_label)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Step list and controls
        left_panel = self.create_step_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Step editor
        right_panel = self.create_step_editor_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (40% left, 60% right)
        splitter.setSizes([400, 600])
        
    def create_step_list_panel(self):
        """Create the step list panel."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setMinimumWidth(350)
        
        layout = QVBoxLayout(panel)
        
        # Header
        header_label = QLabel("Sequence Steps")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #333333;
                padding: 4px;
                background-color: #F5F5F5;
                border-bottom: 1px solid #CCCCCC;
            }
        """)
        layout.addWidget(header_label)
        
        # Add step controls
        add_controls = QHBoxLayout()
        
        # Add step combo
        self.add_step_combo = QComboBox()
        self.add_step_combo.addItem("Select step type to add...")
        for step_type in get_available_step_types():
            widget_class = get_step_widget_class(step_type)
            if widget_class:
                widget_instance = widget_class()
                self.add_step_combo.addItem(f"{widget_instance.get_step_name()}", step_type)
        
        add_controls.addWidget(self.add_step_combo)
        
        # Add step button
        StyledButton = get_widget("StyledButton")
        if StyledButton:
            add_btn = StyledButton("Add")
            add_btn.set_accent_color("#0066CC")
            add_btn.clicked.connect(lambda: self.add_step())
            add_controls.addWidget(add_btn)
        
        layout.addLayout(add_controls)
        
        # Step list
        self.step_list = StepListWidget()
        self.step_list.setSelectionMode(QListWidget.SingleSelection)
        self.step_list.itemSelectionChanged.connect(self.on_step_selection_changed)
        self.step_list.steps_reordered.connect(self.on_steps_reordered)
        self.step_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.step_list.customContextMenuRequested.connect(self.show_step_context_menu)
        layout.addWidget(self.step_list)
        
        # Step control buttons
        button_layout = QHBoxLayout()
        
        if StyledButton:
            # Remove step button
            remove_btn = StyledButton("Remove")
            remove_btn.set_accent_color("#CC0000")
            remove_btn.clicked.connect(self.remove_selected_step)
            button_layout.addWidget(remove_btn)
            
            # Duplicate step button
            duplicate_btn = StyledButton("Duplicate")
            duplicate_btn.clicked.connect(self.duplicate_selected_step)
            button_layout.addWidget(duplicate_btn)
            
            # Clear all button
            clear_btn = StyledButton("Clear All")
            clear_btn.set_accent_color("#FF6600")
            clear_btn.clicked.connect(self.clear_all_steps)
            button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        return panel
        
    def create_step_editor_panel(self):
        """Create the step editor panel."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout(panel)
        
        # Header
        header_label = QLabel("Step Configuration")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #333333;
                padding: 4px;
                background-color: #F5F5F5;
                border-bottom: 1px solid #CCCCCC;
            }
        """)
        layout.addWidget(header_label)
        
        # Stacked widget for step editors
        self.step_widget_stack = QStackedWidget()
        
        # Default empty widget
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_label = QLabel("Select a step from the list to edit its parameters")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-style: italic;
                font-size: 14px;
                padding: 40px;
            }
        """)
        empty_layout.addWidget(empty_label)
        self.step_widget_stack.addWidget(empty_widget)
        
        layout.addWidget(self.step_widget_stack)
        
        return panel
        
    def new_sequence(self):
        """Create a new empty sequence."""
        from .sequence_data_model import SequenceData, SequenceMetadata
        
        metadata = SequenceMetadata(name="New Sequence")
        self._sequence_data = SequenceData(metadata=metadata)
        self._current_step_id = None
        self._is_modified = False
        
        self.refresh_display()
        self.sequence_loaded.emit(self._sequence_data.metadata.name)
        
    def load_sequence(self, sequence_data: SequenceData):
        """
        Load sequence data into the editor.
        
        Args:
            sequence_data: SequenceData object to load
        """
        if not isinstance(sequence_data, SequenceData):
            raise ValueError("sequence_data must be a SequenceData object")
        
        self._sequence_data = sequence_data
        self._current_step_id = None
        self._is_modified = False
        
        self.refresh_display()
        self.sequence_loaded.emit(self._sequence_data.metadata.name)
        
    def get_sequence_data(self) -> Optional[SequenceData]:
        """
        Get the current sequence data from the editor.
        
        Returns:
            SequenceData: Current sequence data structure
        """
        return self._sequence_data
        
    def add_step(self, step_type: str = None, parameters: Dict[str, Any] = None):
        """
        Add a new step to the sequence.
        
        Args:
            step_type (str): Type of step to add (if None, uses combo selection)
            parameters (dict): Step parameters (optional)
        """
        if not self._sequence_data:
            return
            
        if step_type is None:
            # Get from combo box
            current_index = self.add_step_combo.currentIndex()
            if current_index <= 0:  # First item is placeholder
                return
            step_type = self.add_step_combo.itemData(current_index)
        
        if not step_type:
            return
            
        # Create new step
        try:
            step_type_enum = StepType(step_type)
        except ValueError:
            QMessageBox.warning(self, "Invalid Step Type", f"Unknown step type: {step_type}")
            return
            
        new_step = SequenceStep(
            step_type=step_type_enum,
            parameters=parameters or {},
            description=""
        )
        
        # Add to sequence
        step_id = self._sequence_data.add_step(new_step)
        self._is_modified = True
        
        # Refresh display
        self.refresh_step_list()
        
        # Select the new step
        self.select_step_by_id(step_id)
        
        # Reset combo box
        self.add_step_combo.setCurrentIndex(0)
        
        self.sequence_changed.emit()
        
    def remove_step(self, step_id: str):
        """
        Remove a step from the sequence.
        
        Args:
            step_id (str): ID of step to remove
        """
        if not self._sequence_data:
            return
            
        if self._sequence_data.remove_step(step_id):
            self._is_modified = True
            
            # Remove step widget if exists
            if step_id in self.step_widgets:
                widget = self.step_widgets[step_id]
                self.step_widget_stack.removeWidget(widget)
                widget.deleteLater()
                del self.step_widgets[step_id]
            
            # Clear selection if this was the selected step
            if self._current_step_id == step_id:
                self._current_step_id = None
                self.step_widget_stack.setCurrentIndex(0)  # Show empty widget
            
            self.refresh_step_list()
            self.sequence_changed.emit()
            
    def remove_selected_step(self):
        """Remove the currently selected step."""
        if self._current_step_id:
            reply = QMessageBox.question(
                self, "Remove Step", 
                "Are you sure you want to remove this step?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.remove_step(self._current_step_id)
                
    def duplicate_selected_step(self):
        """Duplicate the currently selected step."""
        if not self._current_step_id or not self._sequence_data:
            return
            
        step = self._sequence_data.get_step(self._current_step_id)
        if step:
            # Create a copy of the step
            new_step = SequenceStep(
                step_type=step.step_type,
                parameters=step.parameters.copy(),
                description=step.description + " (Copy)" if step.description else "Copy"
            )
            
            # Add after current step
            current_index = self._sequence_data.get_step_index(self._current_step_id)
            if current_index is not None:
                step_id = self._sequence_data.add_step(new_step, current_index + 1)
                self._is_modified = True
                self.refresh_step_list()
                self.select_step_by_id(step_id)
                self.sequence_changed.emit()
                
    def clear_all_steps(self):
        """Clear all steps from the sequence."""
        if not self._sequence_data or not self._sequence_data.steps:
            return
            
        reply = QMessageBox.question(
            self, "Clear All Steps", 
            "Are you sure you want to remove all steps from the sequence?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._sequence_data.steps.clear()
            self._current_step_id = None
            self._is_modified = True
            
            # Clear all step widgets
            for widget in self.step_widgets.values():
                self.step_widget_stack.removeWidget(widget)
                widget.deleteLater()
            self.step_widgets.clear()
            
            self.refresh_display()
            self.sequence_changed.emit()
            
    def move_step(self, old_index: int, new_index: int):
        """
        Move a step to a new position.
        
        Args:
            old_index: Current position of step
            new_index: New position for step
        """
        if not self._sequence_data or old_index == new_index:
            return
            
        if 0 <= old_index < len(self._sequence_data.steps) and 0 <= new_index < len(self._sequence_data.steps):
            step = self._sequence_data.steps[old_index]
            if self._sequence_data.move_step(step.step_id, new_index):
                self._is_modified = True
                self.sequence_changed.emit()
                
    def refresh_display(self):
        """Refresh the entire display."""
        self.refresh_sequence_info()
        self.refresh_step_list()
        
    def refresh_sequence_info(self):
        """Refresh the sequence information display."""
        if not self._sequence_data:
            self.sequence_info_label.setText("No sequence loaded")
            return
            
        name = self._sequence_data.metadata.name
        step_count = len(self._sequence_data.steps)
        modified_text = " (Modified)" if self._is_modified else ""
        
        info_text = f"Sequence: {name} - {step_count} steps{modified_text}"
        self.sequence_info_label.setText(info_text)
        
    def refresh_step_list(self):
        """Refresh the step list display."""
        # Remember current selection
        current_step_id = self._current_step_id
        
        # Clear list
        self.step_list.clear()
        
        # Add steps
        if self._sequence_data:
            for step in self._sequence_data.steps:
                item = StepListItem(step)
                self.step_list.addItem(item)
                
                # Restore selection
                if step.step_id == current_step_id:
                    self.step_list.setCurrentItem(item)
                    
        self.refresh_sequence_info()
        
    def select_step_by_id(self, step_id: str):
        """Select a step by its ID."""
        for i in range(self.step_list.count()):
            item = self.step_list.item(i)
            if isinstance(item, StepListItem) and item.step.step_id == step_id:
                self.step_list.setCurrentItem(item)
                break
                
    def on_step_selection_changed(self):
        """Handle step selection changes."""
        current_item = self.step_list.currentItem()
        
        if isinstance(current_item, StepListItem):
            step = current_item.step
            self._current_step_id = step.step_id
            self.show_step_editor(step)
            self.step_selected.emit(step.step_id)
        else:
            self._current_step_id = None
            self.step_widget_stack.setCurrentIndex(0)  # Show empty widget
            
    def show_step_editor(self, step: SequenceStep):
        """Show the editor for a specific step."""
        step_id = step.step_id
        
        # Get or create step widget
        if step_id not in self.step_widgets:
            widget = create_step_widget(step.step_type.value)
            if widget:
                # Connect parameter change signal
                widget.parameters_changed.connect(self.on_step_parameters_changed)
                
                # Add to stack
                self.step_widget_stack.addWidget(widget)
                self.step_widgets[step_id] = widget
            else:
                return
        
        widget = self.step_widgets[step_id]
        
        # Update widget with step parameters
        widget.set_parameters(step.parameters)
        
        # Show the widget
        self.step_widget_stack.setCurrentWidget(widget)
        
    def on_step_parameters_changed(self):
        """Handle step parameter changes."""
        if not self._current_step_id or not self._sequence_data:
            return
            
        # Get current step and widget
        step = self._sequence_data.get_step(self._current_step_id)
        widget = self.step_widgets.get(self._current_step_id)
        
        if step and widget:
            # Update step parameters
            step.parameters = widget.get_parameters()
            step.description = widget.get_parameters().get('description', '')
            
            self._is_modified = True
            
            # Update display
            current_item = self.step_list.currentItem()
            if isinstance(current_item, StepListItem):
                current_item.update_display()
                
            self.refresh_sequence_info()
            self.sequence_changed.emit()
            
    def on_steps_reordered(self, old_index: int, new_index: int):
        """Handle step reordering via drag and drop."""
        self.move_step(old_index, new_index)
        
    def show_step_context_menu(self, position):
        """Show context menu for step list."""
        item = self.step_list.itemAt(position)
        if not isinstance(item, StepListItem):
            return
            
        menu = QMenu(self)
        
        # Edit action
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(lambda: self.step_list.setCurrentItem(item))
        menu.addAction(edit_action)
        
        # Duplicate action
        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_step(item.step.step_id))
        menu.addAction(duplicate_action)
        
        menu.addSeparator()
        
        # Remove action
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(lambda: self.remove_step(item.step.step_id))
        menu.addAction(remove_action)
        
        menu.exec_(self.step_list.mapToGlobal(position))
        
    def duplicate_step(self, step_id: str):
        """Duplicate a specific step."""
        if not self._sequence_data:
            return
            
        step = self._sequence_data.get_step(step_id)
        if step:
            # Create a copy of the step
            new_step = SequenceStep(
                step_type=step.step_type,
                parameters=step.parameters.copy(),
                description=step.description + " (Copy)" if step.description else "Copy"
            )
            
            # Add after current step
            current_index = self._sequence_data.get_step_index(step_id)
            if current_index is not None:
                new_step_id = self._sequence_data.add_step(new_step, current_index + 1)
                self._is_modified = True
                self.refresh_step_list()
                self.select_step_by_id(new_step_id)
                self.sequence_changed.emit()
                
    def is_modified(self) -> bool:
        """Check if the sequence has been modified."""
        return self._is_modified
        
    def set_modified(self, modified: bool):
        """Set the modified state."""
        self._is_modified = modified
        self.refresh_sequence_info()
        
    def validate_sequence(self) -> tuple[bool, List[str]]:
        """
        Validate the current sequence.
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        if not self._sequence_data:
            return False, ["No sequence loaded"]
            
        return self._sequence_data.validate()
        
    def get_step_count(self) -> int:
        """Get the number of steps in the sequence."""
        if not self._sequence_data:
            return 0
        return len(self._sequence_data.steps)
        
    def has_steps(self) -> bool:
        """Check if the sequence has any steps."""
        return self.get_step_count() > 0
        
    def get_current_step_id(self) -> Optional[str]:
        """Get the ID of the currently selected step."""
        return self._current_step_id
        
    def load_example_sequence(self):
        """Load an example sequence for testing."""
        example_sequence = create_example_sequence()
        self.load_sequence(example_sequence)
