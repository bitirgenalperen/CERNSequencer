#!/usr/bin/env python3
"""
Sequencer UI Application

Main application for editing and executing operational sequences within 
CERN's particle accelerator control domain.
"""

import sys
import os

# Add the parent directory to the path so we can import pyui
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QMenuBar, QMenu, QAction, QStatusBar, QToolBar,
                             QSplitter, QTextEdit, QLabel, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QKeySequence

from pyui.pyui import ApplicationBase
from pyui.pyui import get_widget
from .sequence_editor import SequenceEditor
from .sequence_data_model import create_example_sequence
from .file_manager import FileManager


class SequencerMainWindow(QMainWindow):
    """Main window for the Sequencer UI application."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.sequence_editor = None
        self.properties_content = None
        self.file_manager = None
        
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_status_bar()
        
        # Initialize file manager
        self.file_manager = FileManager(parent_widget=self)
        
        # Connect sequence editor signals
        self.connect_sequence_editor_signals()
        
    def setup_ui(self):
        """Set up the main UI layout."""
        # Set window properties
        self.setWindowTitle("CERN Sequencer UI")
        self.setMinimumSize(1000, 700)
        
        # Create central widget with splitter layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create horizontal splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Sequence Editor
        self.sequence_editor = SequenceEditor()
        splitter.addWidget(self.sequence_editor)
        
        # Right panel - Properties/Details
        self.properties_frame = self.create_properties_panel()
        splitter.addWidget(self.properties_frame)
        
        # Set splitter proportions (70% left, 30% right)
        splitter.setSizes([700, 300])
        
    def create_properties_panel(self):
        """Create the properties/details panel."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setMaximumWidth(400)
        
        layout = QVBoxLayout(frame)
        
        # Header
        header_label = QLabel("Sequence Properties")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #0066CC;
                padding: 5px;
                background-color: #F0F0F0;
                border-bottom: 1px solid #CCCCCC;
            }
        """)
        layout.addWidget(header_label)
        
        # Properties content
        self.properties_content = QTextEdit()
        self.properties_content.setReadOnly(True)
        self.properties_content.setPlaceholderText(
            "Sequence properties and step details will appear here...\n\n"
            "Select a sequence step to view its configuration."
        )
        layout.addWidget(self.properties_content)
        
        return frame
        
    def connect_sequence_editor_signals(self):
        """Connect sequence editor signals to update the UI."""
        if self.sequence_editor:
            self.sequence_editor.sequence_changed.connect(self.on_sequence_changed)
            self.sequence_editor.sequence_loaded.connect(self.on_sequence_loaded)
            self.sequence_editor.step_selected.connect(self.on_step_selected)
        
    def setup_menu_bar(self):
        """Set up the application menu bar."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('&File')
        
        # New action
        self.new_action = QAction('&New Sequence', self)
        self.new_action.setShortcut(QKeySequence.New)
        self.new_action.setStatusTip('Create a new sequence')
        self.new_action.triggered.connect(self.on_new_sequence)
        file_menu.addAction(self.new_action)
        
        # Open action
        self.open_action = QAction('&Open Sequence...', self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.open_action.setStatusTip('Open an existing sequence file')
        self.open_action.triggered.connect(self.on_open_sequence)
        file_menu.addAction(self.open_action)
        
        file_menu.addSeparator()
        
        # Save action
        self.save_action = QAction('&Save Sequence', self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.setStatusTip('Save the current sequence')
        self.save_action.triggered.connect(self.on_save_sequence)
        file_menu.addAction(self.save_action)
        
        # Save As action
        self.save_as_action = QAction('Save Sequence &As...', self)
        self.save_as_action.setShortcut(QKeySequence.SaveAs)
        self.save_as_action.setStatusTip('Save the sequence with a new name')
        self.save_as_action.triggered.connect(self.on_save_as_sequence)
        file_menu.addAction(self.save_as_action)
        
        file_menu.addSeparator()
        
        # Load Example action
        self.load_example_action = QAction('Load &Example Sequence', self)
        self.load_example_action.setStatusTip('Load an example sequence for testing')
        self.load_example_action.triggered.connect(self.on_load_example_sequence)
        file_menu.addAction(self.load_example_action)
        
        file_menu.addSeparator()
        
        # Recent Files submenu
        self.recent_files_menu = file_menu.addMenu('Recent &Files')
        self.update_recent_files_menu()
        
        file_menu.addSeparator()
        
        # Export submenu
        export_menu = file_menu.addMenu('&Export')
        
        self.export_json_action = QAction('Export as &JSON...', self)
        self.export_json_action.setStatusTip('Export sequence as JSON file')
        self.export_json_action.triggered.connect(self.on_export_json)
        export_menu.addAction(self.export_json_action)
        
        self.export_yaml_action = QAction('Export as &YAML...', self)
        self.export_yaml_action.setStatusTip('Export sequence as YAML file')
        self.export_yaml_action.triggered.connect(self.on_export_yaml)
        export_menu.addAction(self.export_yaml_action)
        
        file_menu.addSeparator()
        
        # Exit action
        self.exit_action = QAction('E&xit', self)
        self.exit_action.setShortcut(QKeySequence.Quit)
        self.exit_action.setStatusTip('Exit the application')
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)
        
        # Sequence Menu
        sequence_menu = menubar.addMenu('&Sequence')
        
        # Run action
        self.run_action = QAction('&Run Sequence', self)
        self.run_action.setShortcut(Qt.Key_F5)
        self.run_action.setStatusTip('Execute the current sequence')
        self.run_action.triggered.connect(self.on_run_sequence)
        sequence_menu.addAction(self.run_action)
        
        # Stop action
        self.stop_action = QAction('&Stop Execution', self)
        self.stop_action.setShortcut(Qt.Key_F6)
        self.stop_action.setStatusTip('Stop sequence execution')
        self.stop_action.setEnabled(False)  # Disabled by default
        self.stop_action.triggered.connect(self.on_stop_sequence)
        sequence_menu.addAction(self.stop_action)
        
        sequence_menu.addSeparator()
        
        # Validate action
        self.validate_action = QAction('&Validate Sequence', self)
        self.validate_action.setShortcut(Qt.Key_F7)
        self.validate_action.setStatusTip('Validate the current sequence')
        self.validate_action.triggered.connect(self.on_validate_sequence)
        sequence_menu.addAction(self.validate_action)
        
        # Add Step submenu
        add_step_menu = sequence_menu.addMenu('&Add Step')
        
        self.add_parameter_action = QAction('Set &Parameter', self)
        self.add_parameter_action.setStatusTip('Add a parameter setting step')
        self.add_parameter_action.triggered.connect(self.on_add_parameter_step)
        add_step_menu.addAction(self.add_parameter_action)
        
        self.add_wait_action = QAction('&Wait for Event', self)
        self.add_wait_action.setStatusTip('Add a wait for event step')
        self.add_wait_action.triggered.connect(self.on_add_wait_step)
        add_step_menu.addAction(self.add_wait_action)
        
        self.add_delay_action = QAction('&Delay', self)
        self.add_delay_action.setStatusTip('Add a delay step')
        self.add_delay_action.triggered.connect(self.on_add_delay_step)
        add_step_menu.addAction(self.add_delay_action)
        
        self.add_diagnostic_action = QAction('Run &Diagnostic', self)
        self.add_diagnostic_action.setStatusTip('Add a diagnostic test step')
        self.add_diagnostic_action.triggered.connect(self.on_add_diagnostic_step)
        add_step_menu.addAction(self.add_diagnostic_action)
        
        self.add_log_action = QAction('&Log Message', self)
        self.add_log_action.setStatusTip('Add a log message step')
        self.add_log_action.triggered.connect(self.on_add_log_step)
        add_step_menu.addAction(self.add_log_action)
        
        # Help Menu
        help_menu = menubar.addMenu('&Help')
        
        self.about_action = QAction('&About Sequencer UI', self)
        self.about_action.setStatusTip('About this application')
        self.about_action.triggered.connect(self.on_about)
        help_menu.addAction(self.about_action)
        
    def setup_toolbar(self):
        """Set up the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        # Get StyledButton from PyUI registry
        StyledButton = get_widget("StyledButton")
        
        if StyledButton:
            # New button
            new_btn = StyledButton("New")
            new_btn.setToolTip("Create a new sequence (Ctrl+N)")
            new_btn.clicked.connect(self.on_new_sequence)
            toolbar.addWidget(new_btn)
            
            # Open button
            open_btn = StyledButton("Open")
            open_btn.setToolTip("Open an existing sequence (Ctrl+O)")
            open_btn.clicked.connect(self.on_open_sequence)
            toolbar.addWidget(open_btn)
            
            # Save button
            save_btn = StyledButton("Save")
            save_btn.setToolTip("Save the current sequence (Ctrl+S)")
            save_btn.clicked.connect(self.on_save_sequence)
            toolbar.addWidget(save_btn)
            
            toolbar.addSeparator()
            
            # Example button
            example_btn = StyledButton("Example")
            example_btn.setToolTip("Load an example sequence")
            example_btn.clicked.connect(self.on_load_example_sequence)
            toolbar.addWidget(example_btn)
            
            # Validate button
            validate_btn = StyledButton("Validate")
            validate_btn.setToolTip("Validate the sequence (F7)")
            validate_btn.clicked.connect(self.on_validate_sequence)
            toolbar.addWidget(validate_btn)
            
            toolbar.addSeparator()
            
            # Run button (with accent color)
            run_btn = StyledButton("Run")
            run_btn.set_accent_color("#00AA00")  # Green for run
            run_btn.setToolTip("Execute the sequence (F5)")
            run_btn.clicked.connect(self.on_run_sequence)
            toolbar.addWidget(run_btn)
            
            # Stop button (with accent color)
            self.stop_btn = StyledButton("Stop")
            self.stop_btn.set_accent_color("#CC0000")  # Red for stop
            self.stop_btn.setToolTip("Stop execution (F6)")
            self.stop_btn.setEnabled(False)
            self.stop_btn.clicked.connect(self.on_stop_sequence)
            toolbar.addWidget(self.stop_btn)
        
    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status message
        self.status_bar.showMessage("Ready - Create a new sequence or open an existing one")
        
        # Add permanent widgets to status bar
        self.sequence_status_label = QLabel("New sequence")
        self.sequence_status_label.setStyleSheet("padding: 2px 10px;")
        self.status_bar.addPermanentWidget(self.sequence_status_label)
        
    # Sequence editor event handlers
    def on_sequence_changed(self):
        """Handle sequence changes."""
        if self.sequence_editor:
            # Update window title
            sequence_data = self.sequence_editor.get_sequence_data()
            if sequence_data:
                modified_text = " *" if self.sequence_editor.is_modified() else ""
                self.setWindowTitle(f"CERN Sequencer UI - {sequence_data.metadata.name}{modified_text}")
            
            # Update properties panel
            self.update_properties_panel()
            
    def on_sequence_loaded(self, sequence_name: str):
        """Handle sequence loading."""
        self.status_bar.showMessage(f"Loaded sequence: {sequence_name}")
        self.sequence_status_label.setText(f"Sequence: {sequence_name}")
        self.setWindowTitle(f"CERN Sequencer UI - {sequence_name}")
        
        # Update properties panel
        self.update_properties_panel()
        
        # Update recent files menu
        self.update_recent_files_menu()
        
    def on_step_selected(self, step_id: str):
        """Handle step selection."""
        if self.sequence_editor:
            sequence_data = self.sequence_editor.get_sequence_data()
            if sequence_data:
                step = sequence_data.get_step(step_id)
                if step:
                    self.update_step_properties(step)
                    
    def update_properties_panel(self):
        """Update the properties panel with sequence information."""
        if not self.sequence_editor:
            return
            
        sequence_data = self.sequence_editor.get_sequence_data()
        if not sequence_data:
            self.properties_content.setText("No sequence loaded")
            return
            
        # Build properties text
        properties_text = f"Sequence: {sequence_data.metadata.name}\n"
        properties_text += f"Description: {sequence_data.metadata.description}\n"
        properties_text += f"Author: {sequence_data.metadata.author}\n"
        properties_text += f"Version: {sequence_data.metadata.version}\n"
        properties_text += f"Category: {sequence_data.metadata.category}\n"
        properties_text += f"Created: {sequence_data.metadata.created_at}\n"
        properties_text += f"Modified: {sequence_data.metadata.modified_at}\n"
        properties_text += f"Tags: {', '.join(sequence_data.metadata.tags)}\n\n"
        
        properties_text += f"Steps: {len(sequence_data.steps)}\n"
        properties_text += f"Variables: {len(sequence_data.variables)}\n\n"
        
        # Validation status
        is_valid, errors = sequence_data.validate()
        properties_text += f"Validation: {'✓ Valid' if is_valid else '✗ Invalid'}\n"
        if errors:
            properties_text += "Errors:\n"
            for error in errors:
                properties_text += f"  - {error}\n"
        
        self.properties_content.setText(properties_text)
        
    def update_step_properties(self, step):
        """Update the properties panel with step information."""
        properties_text = f"Step: {step.step_type.value}\n"
        properties_text += f"ID: {step.step_id}\n"
        properties_text += f"Enabled: {'Yes' if step.enabled else 'No'}\n"
        properties_text += f"Status: {step.status.value}\n"
        properties_text += f"Description: {step.description}\n\n"
        
        properties_text += "Parameters:\n"
        for key, value in step.parameters.items():
            properties_text += f"  {key}: {value}\n"
        
        if step.timeout:
            properties_text += f"\nTimeout: {step.timeout}s\n"
        if step.retry_count > 0:
            properties_text += f"Retry Count: {step.retry_count}\n"
        if step.execution_time:
            properties_text += f"Execution Time: {step.execution_time}s\n"
        if step.error_message:
            properties_text += f"Error: {step.error_message}\n"
        
        self.properties_content.setText(properties_text)
        
    # Action handlers
    def on_new_sequence(self):
        """Handle new sequence action."""
        if self.sequence_editor:
            # Check if current sequence is modified
            if self.sequence_editor.is_modified():
                reply = QMessageBox.question(
                    self, "Unsaved Changes", 
                    "The current sequence has unsaved changes. Do you want to continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            self.sequence_editor.new_sequence()
            self.status_bar.showMessage("New sequence created")
        
    def on_open_sequence(self):
        """Handle open sequence action."""
        if self.file_manager and self.sequence_editor:
            # Check if current sequence is modified
            if self.sequence_editor.is_modified():
                reply = QMessageBox.question(
                    self, "Unsaved Changes", 
                    "The current sequence has unsaved changes. Do you want to continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            # Load sequence
            sequence_data = self.file_manager.load_sequence()
            if sequence_data:
                self.sequence_editor.load_sequence(sequence_data)
                file_name = self.file_manager.get_current_file_name()
                self.status_bar.showMessage(f"Loaded sequence from {file_name}")
                
                # Update window title
                self.setWindowTitle(f"CERN Sequencer UI - {file_name}")
            else:
                self.status_bar.showMessage("Failed to load sequence")
        
    def on_save_sequence(self):
        """Handle save sequence action."""
        if self.file_manager and self.sequence_editor:
            sequence_data = self.sequence_editor.get_sequence_data()
            if sequence_data:
                current_file = self.file_manager.get_current_file_path()
                if current_file:
                    # Save to current file
                    if self.file_manager.save_sequence(sequence_data, current_file, show_dialog=False):
                        self.sequence_editor.set_modified(False)
                        file_name = self.file_manager.get_current_file_name()
                        self.status_bar.showMessage(f"Saved sequence to {file_name}")
                        
                        # Update window title
                        self.setWindowTitle(f"CERN Sequencer UI - {file_name}")
                    else:
                        self.status_bar.showMessage("Failed to save sequence")
                else:
                    # No current file, show Save As dialog
                    self.on_save_as_sequence()
            else:
                self.status_bar.showMessage("No sequence to save")
        
    def on_save_as_sequence(self):
        """Handle save as sequence action."""
        if self.file_manager and self.sequence_editor:
            sequence_data = self.sequence_editor.get_sequence_data()
            if sequence_data:
                if self.file_manager.save_sequence_as(sequence_data):
                    self.sequence_editor.set_modified(False)
                    file_name = self.file_manager.get_current_file_name()
                    self.status_bar.showMessage(f"Saved sequence as {file_name}")
                    
                    # Update window title
                    self.setWindowTitle(f"CERN Sequencer UI - {file_name}")
                else:
                    self.status_bar.showMessage("Failed to save sequence")
            else:
                self.status_bar.showMessage("No sequence to save")
        
    def on_load_example_sequence(self):
        """Handle load example sequence action."""
        if self.sequence_editor:
            self.sequence_editor.load_example_sequence()
            self.status_bar.showMessage("Example sequence loaded")
        
    def on_validate_sequence(self):
        """Handle validate sequence action."""
        if self.sequence_editor:
            is_valid, errors = self.sequence_editor.validate_sequence()
            if is_valid:
                QMessageBox.information(self, "Validation Result", "Sequence is valid!")
                self.status_bar.showMessage("Sequence validation passed")
            else:
                error_text = "Sequence validation failed:\n\n" + "\n".join(errors)
                QMessageBox.warning(self, "Validation Result", error_text)
                self.status_bar.showMessage("Sequence validation failed")
        
    def on_run_sequence(self):
        """Handle run sequence action."""
        if self.sequence_editor:
            if not self.sequence_editor.has_steps():
                QMessageBox.warning(self, "No Steps", "Cannot run an empty sequence. Please add some steps first.")
                return
                
            # Validate before running
            is_valid, errors = self.sequence_editor.validate_sequence()
            if not is_valid:
                reply = QMessageBox.question(
                    self, "Invalid Sequence", 
                    f"The sequence has validation errors:\n\n{chr(10).join(errors)}\n\nDo you want to run anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            self.status_bar.showMessage("Run sequence action triggered (execution engine not implemented yet)")
            self.stop_btn.setEnabled(True)
            self.stop_action.setEnabled(True)
        
    def on_stop_sequence(self):
        """Handle stop sequence action."""
        self.status_bar.showMessage("Stop sequence action triggered (execution engine not implemented yet)")
        self.stop_btn.setEnabled(False)
        self.stop_action.setEnabled(False)
        
    def on_add_parameter_step(self):
        """Handle add parameter step action."""
        if self.sequence_editor:
            self.sequence_editor.add_step("SetParameter")
            self.status_bar.showMessage("Added Set Parameter step")
        
    def on_add_wait_step(self):
        """Handle add wait step action."""
        if self.sequence_editor:
            self.sequence_editor.add_step("WaitForEvent")
            self.status_bar.showMessage("Added Wait for Event step")
        
    def on_add_delay_step(self):
        """Handle add delay step action."""
        if self.sequence_editor:
            self.sequence_editor.add_step("Delay")
            self.status_bar.showMessage("Added Delay step")
            
    def on_add_diagnostic_step(self):
        """Handle add diagnostic step action."""
        if self.sequence_editor:
            self.sequence_editor.add_step("RunDiagnostic")
            self.status_bar.showMessage("Added Run Diagnostic step")
            
    def on_add_log_step(self):
        """Handle add log step action."""
        if self.sequence_editor:
            self.sequence_editor.add_step("LogMessage")
            self.status_bar.showMessage("Added Log Message step")
        
    def on_export_json(self):
        """Handle export as JSON action."""
        if self.file_manager and self.sequence_editor:
            sequence_data = self.sequence_editor.get_sequence_data()
            if sequence_data:
                if self.file_manager.export_sequence(sequence_data, "json"):
                    self.status_bar.showMessage("Sequence exported as JSON")
                else:
                    self.status_bar.showMessage("Failed to export sequence as JSON")
            else:
                self.status_bar.showMessage("No sequence to export")
                
    def on_export_yaml(self):
        """Handle export as YAML action."""
        if self.file_manager and self.sequence_editor:
            sequence_data = self.sequence_editor.get_sequence_data()
            if sequence_data:
                if self.file_manager.export_sequence(sequence_data, "yaml"):
                    self.status_bar.showMessage("Sequence exported as YAML")
                else:
                    self.status_bar.showMessage("Failed to export sequence as YAML")
            else:
                self.status_bar.showMessage("No sequence to export")
                
    def on_open_recent_file(self, file_path: str):
        """Handle opening a recent file."""
        if self.file_manager and self.sequence_editor:
            # Check if current sequence is modified
            if self.sequence_editor.is_modified():
                reply = QMessageBox.question(
                    self, "Unsaved Changes", 
                    "The current sequence has unsaved changes. Do you want to continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            # Load sequence
            sequence_data = self.file_manager.load_sequence(file_path, show_dialog=False)
            if sequence_data:
                self.sequence_editor.load_sequence(sequence_data)
                file_name = self.file_manager.get_current_file_name()
                self.status_bar.showMessage(f"Loaded sequence from {file_name}")
                
                # Update window title
                self.setWindowTitle(f"CERN Sequencer UI - {file_name}")
                
                # Update recent files menu
                self.update_recent_files_menu()
            else:
                self.status_bar.showMessage(f"Failed to load sequence from {file_path}")
                
    def update_recent_files_menu(self):
        """Update the recent files menu."""
        if not self.file_manager:
            return
            
        # Clear existing actions
        self.recent_files_menu.clear()
        
        # Get recent files
        recent_files = self.file_manager.get_recent_files()
        
        if recent_files:
            for file_path in recent_files:
                file_name = os.path.basename(file_path)
                action = QAction(file_name, self)
                action.setStatusTip(f"Open {file_path}")
                action.triggered.connect(lambda checked, path=file_path: self.on_open_recent_file(path))
                self.recent_files_menu.addAction(action)
                
            self.recent_files_menu.addSeparator()
            
            # Add clear recent files action
            clear_action = QAction("Clear Recent Files", self)
            clear_action.triggered.connect(self.on_clear_recent_files)
            self.recent_files_menu.addAction(clear_action)
        else:
            # No recent files
            no_files_action = QAction("No recent files", self)
            no_files_action.setEnabled(False)
            self.recent_files_menu.addAction(no_files_action)
            
    def on_clear_recent_files(self):
        """Handle clearing recent files."""
        if self.file_manager:
            self.file_manager.clear_recent_files()
            self.update_recent_files_menu()
            self.status_bar.showMessage("Recent files cleared")

    def on_about(self):
        """Handle about action."""
        QMessageBox.about(self, "About Sequencer UI", 
                         "CERN Sequencer UI\n\n"
                         "A PyQt-based application for editing and executing\n"
                         "operational sequences for particle accelerator control.\n\n"
                         "Built with PyUI Framework\n"
                         "Version 0.1.0")


class SequencerApp(ApplicationBase):
    """Main Sequencer UI application class."""
    
    def __init__(self):
        super().__init__(
            app_name="CERN Sequencer UI",
            app_version="0.1.0"
        )
        self.main_window = None
        
    def create_main_window(self):
        """Create the main application window."""
        self.main_window = SequencerMainWindow()
        return self.main_window


def main():
    """Main entry point for the Sequencer UI application."""
    app = SequencerApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
