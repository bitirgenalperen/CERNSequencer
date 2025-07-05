#!/usr/bin/env python3
"""
PyUI Hello World Example

This is a minimal example demonstrating how to create a simple PyUI application.
This example shows:
1. How to inherit from PyUI.ApplicationBase
2. How to create a basic window layout
3. How to use PyUI widgets (StyledButton)
4. How to handle events and interactions

This example fulfills the requirement for Milestone 1, Step 4:
"Provide a minimal 'Hello World' example using PyUI."
"""

import sys
import os

# Add the parent directory to the path so we can import pyui
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from pyui.pyui import ApplicationBase, get_widget


class HelloWorldWindow(QWidget):
    """Simple window demonstrating PyUI usage."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the window layout and widgets."""
        # Set window properties
        self.setWindowTitle("PyUI Hello World Example")
        self.setMinimumSize(400, 300)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title label
        title_label = QLabel("Hello, PyUI Framework!")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0066CC; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Description label
        desc_label = QLabel(
            "This is a minimal PyUI application demonstrating:\n"
            "• PyUI.ApplicationBase usage\n"
            "• PyUI widget integration\n"
            "• CERN-themed styling\n"
            "• Event handling"
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #333333; margin-bottom: 20px;")
        main_layout.addWidget(desc_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Get StyledButton from PyUI registry
        StyledButton = get_widget("StyledButton")
        
        if StyledButton:
            # Hello button
            hello_btn = StyledButton("Say Hello")
            hello_btn.clicked.connect(self.on_hello_clicked)
            button_layout.addWidget(hello_btn)
            
            # Clear button
            clear_btn = StyledButton("Clear")
            clear_btn.set_accent_color("#CC6600")  # Orange color
            clear_btn.clicked.connect(self.on_clear_clicked)
            button_layout.addWidget(clear_btn)
            
            # Exit button
            exit_btn = StyledButton("Exit")
            exit_btn.set_accent_color("#CC0000")  # Red color
            exit_btn.clicked.connect(self.close)
            button_layout.addWidget(exit_btn)
        else:
            # Fallback if StyledButton is not available
            fallback_label = QLabel("PyUI StyledButton not available")
            fallback_label.setStyleSheet("color: #CC0000;")
            button_layout.addWidget(fallback_label)
            
        main_layout.addLayout(button_layout)
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setMaximumHeight(100)
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Output will appear here...")
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #F8F8F8;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 5px;
                font-family: monospace;
            }
        """)
        main_layout.addWidget(self.output_text)
        
        # Status label
        self.status_label = QLabel("Ready - Click 'Say Hello' to start!")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-style: italic;
                padding: 5px;
                background-color: #F0F0F0;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        self.hello_count = 0
        
    def on_hello_clicked(self):
        """Handle hello button click."""
        self.hello_count += 1
        message = f"Hello from PyUI! (Click #{self.hello_count})"
        
        # Add to output
        self.output_text.append(message)
        
        # Update status
        self.status_label.setText(f"Said hello {self.hello_count} time(s)")
        
        # Show some PyUI info
        if self.hello_count == 1:
            self.output_text.append("PyUI Framework is working correctly!")
            
            # Show available widgets
            import pyui.pyui as pyui_module
            widgets = pyui_module.list_widgets()
            self.output_text.append(f"Available PyUI widgets: {widgets}")
            
    def on_clear_clicked(self):
        """Handle clear button click."""
        self.output_text.clear()
        self.hello_count = 0
        self.status_label.setText("Output cleared - Ready for new messages!")


class HelloWorldApp(ApplicationBase):
    """Hello World PyUI application."""
    
    def __init__(self):
        super().__init__(
            app_name="PyUI Hello World",
            app_version="1.0.0"
        )
        
    def create_main_window(self, window_class=None):
        """Create the main window."""
        self.main_window = HelloWorldWindow()
        return self.main_window
        
    def setup_ui(self):
        """UI setup is handled by HelloWorldWindow."""
        pass  # All UI setup is done in HelloWorldWindow.__init__


def main():
    """Main entry point for the Hello World example."""
    print("=" * 50)
    print("PyUI Hello World Example")
    print("=" * 50)
    print()
    print("This example demonstrates:")
    print("  ✓ PyUI.ApplicationBase usage")
    print("  ✓ PyUI widget integration")
    print("  ✓ CERN-themed styling")
    print("  ✓ Event handling")
    print("  ✓ Basic application structure")
    print()
    
    # Create and run the application
    app = HelloWorldApp()
    
    print(f"Starting {app.app_name} v{app.app_version}")
    print("Close the window to exit.")
    print()
    
    return app.run()


if __name__ == "__main__":
    sys.exit(main()) 