"""
Unit tests for File Manager module.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestFileManager(unittest.TestCase):
    """Test cases for the FileManager class."""
    
    def test_file_manager_import(self):
        """Test that FileManager can be imported."""
        from sequencer_ui.file_manager import FileManager
        self.assertIsNotNone(FileManager)
        
    def test_file_manager_initialization(self):
        """Test FileManager initialization."""
        from sequencer_ui.file_manager import FileManager
        
        # Test default initialization
        fm = FileManager()
        self.assertIsNotNone(fm.default_directory)
        self.assertIsNone(fm.current_file_path)
        self.assertIsInstance(fm.supported_formats, list)
        
        # Test custom directory initialization
        custom_dir = "/tmp/test_sequences"
        fm_custom = FileManager(custom_dir)
        self.assertEqual(fm_custom.default_directory, custom_dir)
        
    def test_file_manager_methods_exist(self):
        """Test that all expected methods exist in FileManager."""
        from sequencer_ui.file_manager import FileManager
        
        expected_methods = [
            'save_sequence', 'load_sequence', 'get_current_file_path',
            'set_current_file_path', 'validate_sequence_data',
            'create_backup', 'get_recent_files'
        ]
        
        for method_name in expected_methods:
            self.assertTrue(hasattr(FileManager, method_name),
                          f"Method {method_name} not found in FileManager")
            
    def test_file_manager_methods_callable(self):
        """Test that FileManager methods are callable."""
        from sequencer_ui.file_manager import FileManager
        
        methods_to_test = [
            'save_sequence', 'load_sequence', 'get_current_file_path',
            'set_current_file_path', 'validate_sequence_data',
            'create_backup', 'get_recent_files'
        ]
        
        for method_name in methods_to_test:
            method = getattr(FileManager, method_name, None)
            self.assertIsNotNone(method, f"Method {method_name} should exist")
            self.assertTrue(callable(method), f"Method {method_name} should be callable")
            
    def test_file_manager_placeholder_functionality(self):
        """Test that placeholder methods work without errors."""
        from sequencer_ui.file_manager import FileManager
        
        fm = FileManager()
        
        # Test save_sequence placeholder
        result = fm.save_sequence({"test": "data"})
        self.assertTrue(result)  # Placeholder returns True
        
        # Test load_sequence placeholder
        data = fm.load_sequence()
        self.assertIsInstance(data, dict)
        self.assertIn("name", data)
        self.assertIn("steps", data)
        
        # Test get_current_file_path
        path = fm.get_current_file_path()
        self.assertIsNone(path)  # Initially None
        
        # Test set_current_file_path
        test_path = "/tmp/test.json"
        fm.set_current_file_path(test_path)
        self.assertEqual(fm.get_current_file_path(), test_path)
        
        # Test validate_sequence_data
        valid_data = {"name": "test", "steps": []}
        self.assertTrue(fm.validate_sequence_data(valid_data))
        
        invalid_data = {"invalid": "data"}
        self.assertFalse(fm.validate_sequence_data(invalid_data))
        
        # Test create_backup
        backup_result = fm.create_backup("/tmp/test.json")
        self.assertTrue(backup_result)  # Placeholder returns True
        
        # Test get_recent_files
        recent_files = fm.get_recent_files()
        self.assertIsInstance(recent_files, list)
        
    def test_file_manager_supported_formats(self):
        """Test that supported formats are properly defined."""
        from sequencer_ui.file_manager import FileManager
        
        fm = FileManager()
        self.assertIn('.json', fm.supported_formats)
        self.assertIn('.yaml', fm.supported_formats)
        self.assertIn('.yml', fm.supported_formats)


if __name__ == '__main__':
    unittest.main() 