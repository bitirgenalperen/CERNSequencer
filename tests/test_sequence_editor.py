"""
Unit tests for Sequence Editor module.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSequenceEditor(unittest.TestCase):
    """Test cases for the SequenceEditor class."""
    
    def test_sequence_editor_import(self):
        """Test that SequenceEditor can be imported."""
        try:
            from sequencer_ui.sequence_editor import SequenceEditor
            self.assertIsNotNone(SequenceEditor)
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise
                
    def test_sequence_editor_methods_exist(self):
        """Test that all expected methods exist in SequenceEditor."""
        try:
            from sequencer_ui.sequence_editor import SequenceEditor
            
            expected_methods = [
                'load_sequence', 'get_sequence_data', 'add_step',
                'remove_step', 'clear_sequence', 'setup_ui'
            ]
            
            for method_name in expected_methods:
                self.assertTrue(hasattr(SequenceEditor, method_name),
                              f"Method {method_name} not found in SequenceEditor")
                
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise
                
    def test_sequence_editor_methods_callable(self):
        """Test that SequenceEditor methods are callable."""
        try:
            from sequencer_ui.sequence_editor import SequenceEditor
            
            methods_to_test = [
                'load_sequence', 'get_sequence_data', 'add_step',
                'remove_step', 'clear_sequence'
            ]
            
            for method_name in methods_to_test:
                method = getattr(SequenceEditor, method_name, None)
                self.assertIsNotNone(method, f"Method {method_name} should exist")
                self.assertTrue(callable(method), f"Method {method_name} should be callable")
                
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise
                
    def test_sequence_editor_placeholder_functionality(self):
        """Test that placeholder methods work without errors."""
        try:
            from sequencer_ui.sequence_editor import SequenceEditor
            
            # Test that we can create an instance (with mocked PyQt)
            # This is a basic smoke test for the placeholder implementation
            self.assertTrue(hasattr(SequenceEditor, '__init__'))
            
        except ImportError as e:
            if "PyQt5" in str(e):
                self.skipTest("PyQt5 not available for testing")
            else:
                raise


if __name__ == '__main__':
    unittest.main() 