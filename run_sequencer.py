#!/usr/bin/env python3
"""
CERN Sequencer UI Launcher

Simple launcher script for the CERN Sequencer UI application.
This script properly handles imports and provides an easy way to run the application.
"""

import sys
import os

# Add the current directory to Python path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Launch the CERN Sequencer UI application."""
    try:
        from sequencer_ui.sequencer_app import SequencerApp
        
        print("Starting CERN Sequencer UI...")
        print("=" * 50)
        
        # Create and run the application
        app = SequencerApp()
        return app.run()
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("\nMake sure you have installed the required dependencies:")
        print("  pip install pyqt5 pytest pyyaml")
        return 1
        
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 