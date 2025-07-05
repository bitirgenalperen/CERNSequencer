"""
Example Widget for PyUI

Demonstrates how to create custom widgets within the PyUI framework.
"""

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont


class StyledButton(QPushButton):
    """A custom styled button widget for PyUI applications.
    
    This button provides CERN-themed styling and enhanced functionality
    suitable for accelerator control applications.
    """
    
    # Custom signal for enhanced button interactions
    double_clicked = pyqtSignal()
    
    def __init__(self, text="PyUI Button", parent=None):
        """Initialize the styled button.
        
        Args:
            text (str): Button text
            parent: Parent widget
        """
        super().__init__(text, parent)
        self._setup_styling()
        self._setup_behavior()
        
    def _setup_styling(self):
        """Set up the visual styling for the button."""
        # Set a professional font
        font = QFont("Arial", 10, QFont.Bold)
        self.setFont(font)
        
        # Apply CERN-inspired styling
        self.setStyleSheet("""
            StyledButton {
                background-color: #0066CC;
                color: white;
                border: 2px solid #004499;
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 100px;
                min-height: 30px;
            }
            StyledButton:hover {
                background-color: #0080FF;
                border-color: #0066CC;
            }
            StyledButton:pressed {
                background-color: #004499;
                border-color: #003366;
            }
            StyledButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
                border-color: #999999;
            }
        """)
        
    def _setup_behavior(self):
        """Set up enhanced button behavior."""
        # Enable tooltip
        self.setToolTip("PyUI Styled Button - Double-click for special action")
        
        # Track double-click timing
        self._click_timer = None
        
    def mouseDoubleClickEvent(self, event):
        """Handle double-click events."""
        super().mouseDoubleClickEvent(event)
        self.double_clicked.emit()
        
    def set_accent_color(self, color):
        """Set a custom accent color for the button.
        
        Args:
            color (str): CSS color value (e.g., "#FF0000", "red")
        """
        self.setStyleSheet(f"""
            StyledButton {{
                background-color: {color};
                color: white;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 100px;
                min-height: 30px;
            }}
            StyledButton:hover {{
                background-color: {color};
                opacity: 0.8;
            }}
            StyledButton:pressed {{
                background-color: {color};
                opacity: 0.6;
            }}
            StyledButton:disabled {{
                background-color: #CCCCCC;
                color: #666666;
                border-color: #999999;
            }}
        """)
        
    def set_size(self, size_preset):
        """Set button size using presets.
        
        Args:
            size_preset (str): "small", "medium", "large"
        """
        size_configs = {
            "small": {"min_width": 80, "min_height": 25, "font_size": 9},
            "medium": {"min_width": 100, "min_height": 30, "font_size": 10},
            "large": {"min_width": 120, "min_height": 40, "font_size": 12}
        }
        
        if size_preset in size_configs:
            config = size_configs[size_preset]
            self.setMinimumSize(config["min_width"], config["min_height"])
            
            font = self.font()
            font.setPointSize(config["font_size"])
            self.setFont(font)
