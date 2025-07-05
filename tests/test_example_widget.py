"""
Unit tests for PyUI StyledButton widget.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import pyui
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestWidgetRegistry(unittest.TestCase):
    """Test cases for widget registration functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear any existing registry
        import pyui.pyui as pyui_module
        pyui_module._widget_registry.clear()
        
    def test_register_widget(self):
        """Test widget registration functionality."""
        from pyui.pyui import register_widget, get_widget, list_widgets
        
        # Create a dummy widget class
        class DummyWidget:
            pass
            
        # Register the widget
        register_widget("DummyWidget", DummyWidget)
        
        # Verify it was registered
        self.assertIn("DummyWidget", list_widgets())
        self.assertEqual(get_widget("DummyWidget"), DummyWidget)
        
    def test_get_nonexistent_widget(self):
        """Test getting a widget that doesn't exist."""
        from pyui.pyui import get_widget
        
        result = get_widget("NonExistentWidget")
        self.assertIsNone(result)
        
    def test_list_empty_widgets(self):
        """Test listing widgets when registry is empty."""
        from pyui.pyui import list_widgets
        
        widgets = list_widgets()
        self.assertEqual(widgets, [])
        
    def test_builtin_widget_registration(self):
        """Test that built-in widgets are automatically registered."""
        from pyui.pyui import list_widgets, get_widget, _initialize_builtin_widgets
        
        # Re-initialize built-in widgets since setUp cleared the registry
        _initialize_builtin_widgets()
        
        # The StyledButton should be auto-registered when pyui is imported
        registered_widgets = list_widgets()
        self.assertIn("StyledButton", registered_widgets)
        
        # Check if we can retrieve the widget
        widget_class = get_widget("StyledButton")
        self.assertIsNotNone(widget_class)
        
    def test_widget_registry_persistence(self):
        """Test that widget registry persists across multiple calls."""
        from pyui.pyui import register_widget, get_widget, list_widgets
        
        class TestWidget1:
            pass
            
        class TestWidget2:
            pass
            
        # Register multiple widgets
        register_widget("TestWidget1", TestWidget1)
        register_widget("TestWidget2", TestWidget2)
        
        # Verify both are registered
        widgets = list_widgets()
        self.assertIn("TestWidget1", widgets)
        self.assertIn("TestWidget2", widgets)
        
        # Verify we can retrieve both
        self.assertEqual(get_widget("TestWidget1"), TestWidget1)
        self.assertEqual(get_widget("TestWidget2"), TestWidget2)


class TestStyledButtonBasic(unittest.TestCase):
    """Basic tests for StyledButton functionality that don't require PyQt."""
    
    def test_styled_button_class_exists(self):
        """Test that the StyledButton class can be imported."""
        try:
            from pyui.pyui.widgets.example_widget import StyledButton
            self.assertIsNotNone(StyledButton)
        except ImportError as e:
            # If PyQt5 is not available, this is expected
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise
                
    def test_styled_button_has_required_methods(self):
        """Test that StyledButton has the expected methods."""
        try:
            from pyui.pyui.widgets.example_widget import StyledButton
            
            # Check that the class has the expected methods
            self.assertTrue(hasattr(StyledButton, 'set_accent_color'))
            self.assertTrue(hasattr(StyledButton, 'set_size'))
            self.assertTrue(hasattr(StyledButton, 'mouseDoubleClickEvent'))
            
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise


if __name__ == '__main__':
    unittest.main()
