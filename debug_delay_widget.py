#!/usr/bin/env python3
"""
Debug script for DelayWidget validation issue.
"""

import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from sequencer_ui.step_widgets.delay_widget import DelayWidget

def test_delay_widget_validation():
    """Test DelayWidget validation behavior."""
    app = QApplication.instance() or QApplication([])
    widget = DelayWidget()
    
    print("=== DelayWidget Debug ===")
    
    # Test setting negative duration
    print("\n1. Setting duration to -1.0:")
    print(f"   Before set_parameters - Internal duration: {widget._duration}")
    
    widget.set_parameters({"duration": -1.0})
    
    print(f"   After set_parameters - Internal duration: {widget._duration}")
    if widget.duration_spinbox:
        print(f"   Spinbox value: {widget.duration_spinbox.value()}")
        print(f"   Spinbox minimum: {widget.duration_spinbox.minimum()}")
    
    # Check the conversion
    display_duration, display_unit = widget._convert_from_seconds(-1.0)
    print(f"   Convert from seconds result: {display_duration}, {display_unit}")
    
    # Get parameters back
    params = widget.get_parameters()
    print(f"   Retrieved duration: {params.get('duration')}")
    
    # Test validation
    is_valid, errors = widget.validate_parameters()
    print(f"   Validation result: {is_valid}")
    print(f"   Errors: {errors}")
    
    print("\n2. Setting duration directly on internal variable:")
    widget._duration = -1.0
    is_valid, errors = widget.validate_parameters()
    print(f"   Internal duration: {widget._duration}")
    print(f"   Validation result: {is_valid}")
    print(f"   Errors: {errors}")

if __name__ == "__main__":
    test_delay_widget_validation() 