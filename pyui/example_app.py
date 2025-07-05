#!/usr/bin/env python3
"""
PyUI Example Application

Demonstrates how to use the PyUI framework to create a simple application
with custom widgets and the ApplicationBase class.
"""

import sys
import os

# Add the parent directory to the path so we can import pyui
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from pyui import ApplicationBase, get_widget


class ExampleApp(ApplicationBase):
    """Example application demonstrating PyUI usage."""
    
    def __init__(self):
        super().__init__(
            app_name="PyUI Example Application",
            app_version="1.0.0"
        )
        
    def setup_ui(self):
        """Set up the example UI with PyUI widgets."""
        # Create central widget and layout
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Add title
        title_label = QLabel("PyUI Framework Example")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #0066CC;
                margin: 20px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Add description
        desc_label = QLabel(
            "This example demonstrates the PyUI framework capabilities:\n"
            "• ApplicationBase for common PyQt setup\n"
            "• Custom widget registration and usage\n"
            "• CERN-themed styling"
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("margin: 10px; font-size: 12px;")
        main_layout.addWidget(desc_label)
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Get the StyledButton widget class from registry
        StyledButton = get_widget("StyledButton")
        
        if StyledButton:
            # Create different styled buttons
            button1 = StyledButton("Default Button")
            button1.clicked.connect(lambda: self.on_button_click("Default"))
            button1.double_clicked.connect(lambda: self.on_button_double_click("Default"))
            
            button2 = StyledButton("Green Button")
            button2.set_accent_color("#00AA00")
            button2.clicked.connect(lambda: self.on_button_click("Green"))
            
            button3 = StyledButton("Large Red Button")
            button3.set_accent_color("#CC0000")
            button3.set_size("large")
            button3.clicked.connect(lambda: self.on_button_click("Large Red"))
            
            button4 = StyledButton("Small Button")
            button4.set_size("small")
            button4.clicked.connect(lambda: self.on_button_click("Small"))
            
            # Add buttons to layout
            button_layout.addWidget(button1)
            button_layout.addWidget(button2)
            button_layout.addWidget(button3)
            button_layout.addWidget(button4)
        else:
            # Fallback if widget registration fails
            error_label = QLabel("Error: StyledButton widget not found in registry!")
            error_label.setStyleSheet("color: red; font-weight: bold;")
            button_layout.addWidget(error_label)
        
        main_layout.addLayout(button_layout)
        
        # Add status label
        self.status_label = QLabel("Ready - Click buttons to test functionality")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 8px;
                margin: 20px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        # Add stretch to center content
        main_layout.addStretch()
        
    def on_button_click(self, button_name):
        """Handle button click events."""
        self.status_label.setText(f"Clicked: {button_name} button")
        
    def on_button_double_click(self, button_name):
        """Handle button double-click events."""
        self.status_label.setText(f"Double-clicked: {button_name} button!")


def main():
    """Main entry point for the example application."""
    app = ExampleApp()
    
    # Print some information about the PyUI framework
    print("PyUI Example Application Starting...")
    print(f"Application: {app.app_name} v{app.app_version}")
    
    # Import pyui to access registry functions
    import pyui
    print(f"Registered widgets: {pyui.list_widgets()}")
    
    # Run the application
    return app.run()


if __name__ == "__main__":
    sys.exit(main()) 