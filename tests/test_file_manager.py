"""
Unit tests for File Manager module.
"""

import unittest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock

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
        self.assertIsInstance(fm.supported_formats, dict)
        
        # Test custom directory initialization
        custom_dir = "/tmp/test_sequences"
        fm_custom = FileManager(custom_dir)
        self.assertEqual(fm_custom.default_directory, custom_dir)
        
    def test_file_manager_methods_exist(self):
        """Test that all expected methods exist in FileManager."""
        from sequencer_ui.file_manager import FileManager
        
        expected_methods = [
            'save_sequence', 'load_sequence', 'get_current_file_path',
            'set_current_file_path', 'save_sequence_as',
            'create_backup', 'get_recent_files', 'export_sequence'
        ]
        
        for method_name in expected_methods:
            self.assertTrue(hasattr(FileManager, method_name),
                          f"Method {method_name} not found in FileManager")
            
    def test_file_manager_methods_callable(self):
        """Test that FileManager methods are callable."""
        from sequencer_ui.file_manager import FileManager
        
        methods_to_test = [
            'save_sequence', 'load_sequence', 'get_current_file_path',
            'set_current_file_path', 'save_sequence_as',
            'create_backup', 'get_recent_files', 'export_sequence'
        ]
        
        for method_name in methods_to_test:
            method = getattr(FileManager, method_name, None)
            self.assertIsNotNone(method, f"Method {method_name} should exist")
            self.assertTrue(callable(method), f"Method {method_name} should be callable")
            
    def test_file_manager_functionality_with_sequence_data(self):
        """Test that FileManager works with SequenceData objects."""
        from sequencer_ui.file_manager import FileManager
        from sequencer_ui.sequence_data_model import create_example_sequence
        
        with tempfile.TemporaryDirectory() as temp_dir:
            fm = FileManager(default_directory=temp_dir)
            
            # Create test sequence
            sequence = create_example_sequence()
            
            # Test save_sequence with valid SequenceData
            test_file = os.path.join(temp_dir, "test.json")
            result = fm.save_sequence(sequence, test_file, show_dialog=False)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(test_file))
            
            # Test load_sequence
            loaded_sequence = fm.load_sequence(test_file, show_dialog=False)
            self.assertIsNotNone(loaded_sequence)
            self.assertEqual(loaded_sequence.metadata.name, sequence.metadata.name)
            
            # Test current file path tracking
            self.assertEqual(fm.get_current_file_path(), test_file)
            self.assertEqual(fm.get_current_file_name(), "test.json")
            
    def test_file_manager_error_handling(self):
        """Test FileManager error handling."""
        from sequencer_ui.file_manager import FileManager
        
        fm = FileManager()
        
        # Test save_sequence with invalid data
        result = fm.save_sequence("invalid_data", "/tmp/test.json", show_dialog=False)
        self.assertFalse(result)  # Should fail gracefully
        
        # Test load_sequence with non-existent file
        loaded = fm.load_sequence("/nonexistent/file.json", show_dialog=False)
        self.assertIsNone(loaded)  # Should return None
        
    def test_file_manager_recent_files(self):
        """Test recent files functionality."""
        from sequencer_ui.file_manager import FileManager
        
        # Mock QSettings to avoid actual file system operations
        with patch('sequencer_ui.file_manager.QSettings') as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings.return_value = mock_settings_instance
            mock_settings_instance.value.return_value = []
            
            fm = FileManager()
            
            # Test get_recent_files
            recent_files = fm.get_recent_files()
            self.assertIsInstance(recent_files, list)
            
            # Test clear_recent_files
            fm.clear_recent_files()
            mock_settings_instance.setValue.assert_called()
        
    def test_file_manager_supported_formats(self):
        """Test that supported formats are properly defined."""
        from sequencer_ui.file_manager import FileManager
        
        fm = FileManager()
        self.assertIsInstance(fm.supported_formats, dict)
        self.assertIn('.json', fm.supported_formats)
        self.assertIn('.yaml', fm.supported_formats)
        self.assertIn('.yml', fm.supported_formats)
        
    def test_file_manager_backup_functionality(self):
        """Test backup functionality."""
        from sequencer_ui.file_manager import FileManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            fm = FileManager(default_directory=temp_dir)
            
            # Create a test file
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test content")
            
            # Test backup creation
            result = fm.create_backup(test_file)
            self.assertTrue(result)
            
            # Test backup of non-existent file
            result = fm.create_backup("/nonexistent/file.txt")
            self.assertTrue(result)  # Should succeed (no backup needed)


class TestFileManagerIntegration(unittest.TestCase):
    """Integration tests for FileManager with sequence data."""
    
    def test_json_roundtrip(self):
        """Test complete JSON save/load cycle."""
        from sequencer_ui.file_manager import FileManager
        from sequencer_ui.sequence_data_model import create_example_sequence
        
        with tempfile.TemporaryDirectory() as temp_dir:
            fm = FileManager(default_directory=temp_dir)
            original_sequence = create_example_sequence()
            
            # Save as JSON
            json_file = os.path.join(temp_dir, "test.json")
            save_result = fm.save_sequence(original_sequence, json_file, show_dialog=False)
            self.assertTrue(save_result)
            
            # Load from JSON
            loaded_sequence = fm.load_sequence(json_file, show_dialog=False)
            self.assertIsNotNone(loaded_sequence)
            
            # Verify data integrity
            self.assertEqual(loaded_sequence.metadata.name, original_sequence.metadata.name)
            self.assertEqual(len(loaded_sequence.steps), len(original_sequence.steps))
            
            # Verify validation
            is_valid, errors = loaded_sequence.validate()
            self.assertTrue(is_valid)
            
    def test_yaml_roundtrip(self):
        """Test complete YAML save/load cycle (if YAML is available)."""
        from sequencer_ui.file_manager import FileManager, YAML_AVAILABLE
        from sequencer_ui.sequence_data_model import create_example_sequence
        
        if not YAML_AVAILABLE:
            self.skipTest("YAML not available")
            
        with tempfile.TemporaryDirectory() as temp_dir:
            fm = FileManager(default_directory=temp_dir)
            original_sequence = create_example_sequence()
            
            # Save as YAML
            yaml_file = os.path.join(temp_dir, "test.yaml")
            save_result = fm.save_sequence(original_sequence, yaml_file, show_dialog=False)
            self.assertTrue(save_result)
            
            # Load from YAML
            loaded_sequence = fm.load_sequence(yaml_file, show_dialog=False)
            self.assertIsNotNone(loaded_sequence)
            
            # Verify data integrity
            self.assertEqual(loaded_sequence.metadata.name, original_sequence.metadata.name)
            self.assertEqual(len(loaded_sequence.steps), len(original_sequence.steps))


class TestCreateExampleSequenceFile(unittest.TestCase):
    """Test cases for the create_example_sequence_file function."""
    
    def test_create_example_sequence_file(self):
        """Test creating an example sequence file."""
        from sequencer_ui.file_manager import create_example_sequence_file
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "example.json")
            result = create_example_sequence_file(test_file)
            
            self.assertTrue(result)
            self.assertTrue(os.path.exists(test_file))
            
            # Verify file content
            import json
            with open(test_file, 'r') as f:
                data = json.load(f)
            
            self.assertIn('metadata', data)
            self.assertIn('steps', data)
            self.assertGreater(len(data['steps']), 0)


if __name__ == '__main__':
    unittest.main() 