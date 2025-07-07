"""
File Manager Module

This module handles saving and loading sequence data to/from the local file system.
Provides complete file management capabilities including JSON/YAML serialization,
file dialogs, validation, and error handling.

Implementation for Milestone 2 - Development Step 4: Local File Persistence
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget
from PyQt5.QtCore import QSettings

from .sequence_data_model import SequenceData


class FileManager:
    """
    Complete file manager for sequence persistence.
    
    This class provides comprehensive file management capabilities including:
    - JSON and YAML serialization/deserialization
    - PyQt file dialogs for save/load operations
    - File format validation and error recovery
    - Recent files management
    - Automatic backup creation
    """
    
    def __init__(self, default_directory: str = None, parent_widget: QWidget = None):
        """
        Initialize the file manager.
        
        Args:
            default_directory (str): Default directory for sequence files
            parent_widget (QWidget): Parent widget for dialogs
        """
        self.default_directory = default_directory or os.path.expanduser("~/sequences")
        self.parent_widget = parent_widget
        self.current_file_path = None
        self.settings = QSettings("CERN", "SequencerUI")
        
        # Supported file formats
        self.supported_formats = {
            '.json': 'JSON files (*.json)',
            '.yaml': 'YAML files (*.yaml)',
            '.yml': 'YAML files (*.yml)'
        }
        
        # Ensure default directory exists
        self._ensure_directory_exists(self.default_directory)
        
    def save_sequence(self, sequence_data: SequenceData, file_path: str = None, 
                     show_dialog: bool = True) -> bool:
        """
        Save sequence data to a file.
        
        Args:
            sequence_data (SequenceData): Sequence data to save
            file_path (str): Path to save file (optional, will prompt if None)
            show_dialog (bool): Whether to show file dialog if no path provided
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            # Validate sequence data
            if not isinstance(sequence_data, SequenceData):
                raise ValueError("sequence_data must be a SequenceData object")
            
            is_valid, errors = sequence_data.validate()
            if not is_valid:
                if self.parent_widget:
                    QMessageBox.warning(
                        self.parent_widget, "Invalid Sequence",
                        f"Cannot save invalid sequence:\n\n{chr(10).join(errors)}"
                    )
                return False
            
            # Get file path
            if file_path is None:
                if show_dialog:
                    file_path = self._get_save_file_path()
                    if not file_path:
                        return False  # User cancelled
                else:
                    if self.current_file_path:
                        file_path = self.current_file_path
                    else:
                        raise ValueError("No file path provided and no current file")
            
            # Create backup if file exists
            if os.path.exists(file_path):
                if not self.create_backup(file_path):
                    if self.parent_widget:
                        reply = QMessageBox.question(
                            self.parent_widget, "Backup Failed",
                            "Could not create backup. Continue saving anyway?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No
                        )
                        if reply != QMessageBox.Yes:
                            return False
            
            # Update metadata
            sequence_data.metadata.modified_at = datetime.now().isoformat()
            
            # Serialize and save
            file_extension = Path(file_path).suffix.lower()
            if file_extension in ['.yaml', '.yml']:
                success = self._save_yaml(sequence_data, file_path)
            else:
                success = self._save_json(sequence_data, file_path)
            
            if success:
                self.current_file_path = file_path
                self._add_to_recent_files(file_path)
                return True
            
            return False
            
        except Exception as e:
            if self.parent_widget:
                QMessageBox.critical(
                    self.parent_widget, "Save Error",
                    f"Failed to save sequence:\n{str(e)}"
                )
            return False
            
    def load_sequence(self, file_path: str = None, show_dialog: bool = True) -> Optional[SequenceData]:
        """
        Load sequence data from a file.
        
        Args:
            file_path (str): Path to load file (optional, will prompt if None)
            show_dialog (bool): Whether to show file dialog if no path provided
            
        Returns:
            SequenceData: Loaded sequence data, or None if load failed
        """
        try:
            # Get file path
            if file_path is None:
                if show_dialog:
                    file_path = self._get_open_file_path()
                    if not file_path:
                        return None  # User cancelled
                else:
                    raise ValueError("No file path provided")
            
            # Check if file exists
            if not os.path.exists(file_path):
                if self.parent_widget:
                    QMessageBox.warning(
                        self.parent_widget, "File Not Found",
                        f"File not found: {file_path}"
                    )
                return None
            
            # Load and deserialize
            file_extension = Path(file_path).suffix.lower()
            if file_extension in ['.yaml', '.yml']:
                sequence_data = self._load_yaml(file_path)
            else:
                sequence_data = self._load_json(file_path)
            
            if sequence_data:
                # Validate loaded data
                is_valid, errors = sequence_data.validate()
                if not is_valid:
                    if self.parent_widget:
                        reply = QMessageBox.question(
                            self.parent_widget, "Invalid Sequence",
                            f"Loaded sequence has validation errors:\n\n{chr(10).join(errors)}\n\nLoad anyway?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No
                        )
                        if reply != QMessageBox.Yes:
                            return None
                
                self.current_file_path = file_path
                self._add_to_recent_files(file_path)
                return sequence_data
            
            return None
            
        except Exception as e:
            if self.parent_widget:
                QMessageBox.critical(
                    self.parent_widget, "Load Error",
                    f"Failed to load sequence:\n{str(e)}"
                )
            return None
            
    def save_sequence_as(self, sequence_data: SequenceData) -> bool:
        """
        Save sequence with a new file name (Save As dialog).
        
        Args:
            sequence_data (SequenceData): Sequence data to save
            
        Returns:
            bool: True if save successful, False otherwise
        """
        return self.save_sequence(sequence_data, file_path=None, show_dialog=True)
        
    def get_current_file_path(self) -> Optional[str]:
        """
        Get the path of the currently loaded/saved file.
        
        Returns:
            str: Current file path, or None if no file is loaded
        """
        return self.current_file_path
        
    def set_current_file_path(self, file_path: str):
        """
        Set the current file path.
        
        Args:
            file_path (str): Path to set as current
        """
        self.current_file_path = file_path
        
    def get_current_file_name(self) -> Optional[str]:
        """
        Get the name of the currently loaded/saved file.
        
        Returns:
            str: Current file name, or None if no file is loaded
        """
        if self.current_file_path:
            return os.path.basename(self.current_file_path)
        return None
        
    def is_file_modified_externally(self) -> bool:
        """
        Check if the current file has been modified externally.
        
        Returns:
            bool: True if file has been modified externally
        """
        if not self.current_file_path or not os.path.exists(self.current_file_path):
            return False
        
        # This is a simplified check - in a full implementation,
        # we would store and compare file modification times
        return False
        
    def create_backup(self, file_path: str) -> bool:
        """
        Create a backup of an existing file before overwriting.
        
        Args:
            file_path (str): Path to file to backup
            
        Returns:
            bool: True if backup successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                return True  # No need to backup non-existent file
            
            # Create backup filename with timestamp
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_path)
            
            # Keep only the last 5 backups
            self._cleanup_old_backups(file_path)
            
            return True
            
        except Exception as e:
            print(f"Failed to create backup: {e}")
            return False
            
    def get_recent_files(self, max_count: int = 10) -> List[str]:
        """
        Get list of recently opened files.
        
        Args:
            max_count (int): Maximum number of recent files to return
            
        Returns:
            list: List of recent file paths
        """
        recent_files = self.settings.value("recent_files", [])
        if not isinstance(recent_files, list):
            recent_files = []
        
        # Filter out non-existent files
        existing_files = [f for f in recent_files if os.path.exists(f)]
        
        # Update settings if any files were removed
        if len(existing_files) != len(recent_files):
            self.settings.setValue("recent_files", existing_files)
        
        return existing_files[:max_count]
        
    def clear_recent_files(self):
        """Clear the recent files list."""
        self.settings.setValue("recent_files", [])
        
    def export_sequence(self, sequence_data: SequenceData, format_type: str = "json") -> bool:
        """
        Export sequence to a specific format.
        
        Args:
            sequence_data (SequenceData): Sequence data to export
            format_type (str): Export format ('json' or 'yaml')
            
        Returns:
            bool: True if export successful
        """
        try:
            if format_type.lower() == "yaml":
                if not YAML_AVAILABLE:
                    if self.parent_widget:
                        QMessageBox.warning(
                            self.parent_widget, "YAML Not Available",
                            "YAML export requires PyYAML library to be installed."
                        )
                    return False
                
                file_path = self._get_save_file_path(
                    title="Export Sequence as YAML",
                    filter_str="YAML files (*.yaml *.yml)"
                )
            else:
                file_path = self._get_save_file_path(
                    title="Export Sequence as JSON",
                    filter_str="JSON files (*.json)"
                )
            
            if file_path:
                return self.save_sequence(sequence_data, file_path, show_dialog=False)
            
            return False
            
        except Exception as e:
            if self.parent_widget:
                QMessageBox.critical(
                    self.parent_widget, "Export Error",
                    f"Failed to export sequence:\n{str(e)}"
                )
            return False
            
    def _save_json(self, sequence_data: SequenceData, file_path: str) -> bool:
        """Save sequence data as JSON."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sequence_data.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to save JSON: {e}")
            return False
            
    def _save_yaml(self, sequence_data: SequenceData, file_path: str) -> bool:
        """Save sequence data as YAML."""
        if not YAML_AVAILABLE:
            return False
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(sequence_data.to_dict(), f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save YAML: {e}")
            return False
            
    def _load_json(self, file_path: str) -> Optional[SequenceData]:
        """Load sequence data from JSON."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return SequenceData.from_dict(data)
        except Exception as e:
            print(f"Failed to load JSON: {e}")
            return None
            
    def _load_yaml(self, file_path: str) -> Optional[SequenceData]:
        """Load sequence data from YAML."""
        if not YAML_AVAILABLE:
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return SequenceData.from_dict(data)
        except Exception as e:
            print(f"Failed to load YAML: {e}")
            return None
            
    def _get_save_file_path(self, title: str = "Save Sequence", 
                           filter_str: str = None) -> Optional[str]:
        """Get file path for saving using file dialog."""
        if filter_str is None:
            if YAML_AVAILABLE:
                filter_str = "JSON files (*.json);;YAML files (*.yaml *.yml);;All files (*.*)"
            else:
                filter_str = "JSON files (*.json);;All files (*.*)"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent_widget,
            title,
            self.default_directory,
            filter_str
        )
        
        return file_path if file_path else None
        
    def _get_open_file_path(self, title: str = "Open Sequence", 
                           filter_str: str = None) -> Optional[str]:
        """Get file path for opening using file dialog."""
        if filter_str is None:
            if YAML_AVAILABLE:
                filter_str = "Sequence files (*.json *.yaml *.yml);;JSON files (*.json);;YAML files (*.yaml *.yml);;All files (*.*)"
            else:
                filter_str = "Sequence files (*.json);;JSON files (*.json);;All files (*.*)"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent_widget,
            title,
            self.default_directory,
            filter_str
        )
        
        return file_path if file_path else None
        
    def _add_to_recent_files(self, file_path: str):
        """Add file to recent files list."""
        recent_files = self.get_recent_files()
        
        # Remove if already in list
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to beginning
        recent_files.insert(0, file_path)
        
        # Keep only last 10 files
        recent_files = recent_files[:10]
        
        self.settings.setValue("recent_files", recent_files)
        
    def _ensure_directory_exists(self, directory: str):
        """Ensure directory exists, create if necessary."""
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            print(f"Failed to create directory {directory}: {e}")
            
    def _cleanup_old_backups(self, file_path: str):
        """Clean up old backup files, keeping only the last 5."""
        try:
            directory = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            backup_pattern = f"{base_name}.backup_"
            
            # Find all backup files
            backup_files = []
            for file in os.listdir(directory):
                if file.startswith(backup_pattern):
                    backup_files.append(os.path.join(directory, file))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=os.path.getmtime, reverse=True)
            
            # Remove old backups (keep only 5)
            for backup_file in backup_files[5:]:
                try:
                    os.remove(backup_file)
                except Exception as e:
                    print(f"Failed to remove old backup {backup_file}: {e}")
                    
        except Exception as e:
            print(f"Failed to cleanup old backups: {e}")


def create_example_sequence_file(file_path: str) -> bool:
    """
    Create an example sequence file for testing.
    
    Args:
        file_path (str): Path where to create the example file
        
    Returns:
        bool: True if file created successfully
    """
    try:
        from .sequence_data_model import create_example_sequence
        
        file_manager = FileManager()
        example_sequence = create_example_sequence()
        
        return file_manager.save_sequence(example_sequence, file_path, show_dialog=False)
        
    except Exception as e:
        print(f"Failed to create example sequence file: {e}")
        return False
