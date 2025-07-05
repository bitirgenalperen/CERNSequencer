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
                             QSplitter, QTextEdit, QLabel, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QKeySequence

from pyui.pyui import ApplicationBase
from pyui.pyui import get_widget


class SequencerMainWindow(QMainWindow):
    """Main window for the Sequencer UI application."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_status_bar()
        
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
        self.sequence_editor_frame = self.create_sequence_editor_panel()
        splitter.addWidget(self.sequence_editor_frame)
        
        # Right panel - Properties/Details
        self.properties_frame = self.create_properties_panel()
        splitter.addWidget(self.properties_frame)
        
        # Set splitter proportions (70% left, 30% right)
        splitter.setSizes([700, 300])
        
    def create_sequence_editor_panel(self):
        """Create the main sequence editor panel."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout(frame)
        
        # Header
        header_label = QLabel("Sequence Editor")
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
        
        # Placeholder for sequence steps
        self.sequence_content = QTextEdit()
        self.sequence_content.setPlaceholderText(
            "Sequence steps will appear here...\n\n"
            "Use the 'New' button to create a new sequence,\n"
            "or 'Open' to load an existing sequence file."
        )
        self.sequence_content.setReadOnly(True)
        layout.addWidget(self.sequence_content)
        
        return frame
        
    def create_properties_panel(self):
        """Create the properties/details panel."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout(frame)
        
        # Header
        header_label = QLabel("Step Properties")
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
        
        # Placeholder for step properties
        self.properties_content = QTextEdit()
        self.properties_content.setPlaceholderText(
            "Step properties and parameters\nwill be displayed here when\na step is selected."
        )
        self.properties_content.setReadOnly(True)
        layout.addWidget(self.properties_content)
        
        return frame
        
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
        self.sequence_status_label = QLabel("No sequence loaded")
        self.sequence_status_label.setStyleSheet("padding: 2px 10px;")
        self.status_bar.addPermanentWidget(self.sequence_status_label)
        
    # Dummy action handlers (no functionality yet)
    def on_new_sequence(self):
        """Handle new sequence action."""
        self.status_bar.showMessage("New sequence action triggered (not implemented yet)")
        self.sequence_content.setPlainText("New sequence created (placeholder)")
        self.sequence_status_label.setText("New sequence")
        
    def on_open_sequence(self):
        """Handle open sequence action."""
        self.status_bar.showMessage("Open sequence action triggered (not implemented yet)")
        
    def on_save_sequence(self):
        """Handle save sequence action."""
        self.status_bar.showMessage("Save sequence action triggered (not implemented yet)")
        
    def on_save_as_sequence(self):
        """Handle save as sequence action."""
        self.status_bar.showMessage("Save as sequence action triggered (not implemented yet)")
        
    def on_run_sequence(self):
        """Handle run sequence action."""
        self.status_bar.showMessage("Run sequence action triggered (not implemented yet)")
        self.stop_btn.setEnabled(True)
        self.stop_action.setEnabled(True)
        
    def on_stop_sequence(self):
        """Handle stop sequence action."""
        self.status_bar.showMessage("Stop sequence action triggered (not implemented yet)")
        self.stop_btn.setEnabled(False)
        self.stop_action.setEnabled(False)
        
    def on_add_parameter_step(self):
        """Handle add parameter step action."""
        self.status_bar.showMessage("Add parameter step action triggered (not implemented yet)")
        
    def on_add_wait_step(self):
        """Handle add wait step action."""
        self.status_bar.showMessage("Add wait step action triggered (not implemented yet)")
        
    def on_add_delay_step(self):
        """Handle add delay step action."""
        self.status_bar.showMessage("Add delay step action triggered (not implemented yet)")
        
    def on_about(self):
        """Handle about action."""
        self.status_bar.showMessage("About dialog action triggered (not implemented yet)")


class SequencerApp(ApplicationBase):
    """Main Sequencer UI application class."""
    
    def __init__(self):
        super().__init__(
            app_name="CERN Sequencer UI",
            app_version="0.1.0"
        )
        
    def create_main_window(self, window_class=None):
        """Create the main window using SequencerMainWindow."""
        self.main_window = SequencerMainWindow()
        return self.main_window
        
    def setup_ui(self):
        """UI setup is handled by SequencerMainWindow."""
        pass  # All UI setup is done in SequencerMainWindow.__init__


def main():
    """Main entry point for the Sequencer UI application."""
    app = SequencerApp()
    
    print("CERN Sequencer UI Starting...")
    print(f"Application: {app.app_name} v{app.app_version}")
    print("PyUI Framework Integration: Active")
    
    # Import pyui to show registered widgets
    import pyui.pyui as pyui_module
    print(f"Available PyUI widgets: {pyui_module.list_widgets()}")
    
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
