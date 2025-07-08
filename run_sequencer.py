#!/usr/bin/env python3
"""
Run Script for CERN Sequencer UI

This script provides an easy way to start the Sequencer UI application
and load demo sequences for testing and demonstration purposes.
"""

import sys
import os
import argparse

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main function to run the Sequencer UI application."""
    parser = argparse.ArgumentParser(description='Run CERN Sequencer UI')
    parser.add_argument('--demo', action='store_true', 
                       help='Load demo sequence on startup')
    parser.add_argument('--load', type=str, 
                       help='Load specific sequence file on startup')
    
    args = parser.parse_args()
    
    print("🚀 Starting CERN Sequencer UI...")
    print("=" * 50)
    
    try:
        from sequencer_ui.sequencer_app import SequencerApp
        
        # Create and initialize the application (this creates QApplication)
        app = SequencerApp()
        app.initialize_application()
        
        # Now create the main window (after QApplication exists)
        main_window = app.create_main_window()
        
        # Show the main window
        main_window.show()
        print("💻 Sequencer UI started successfully!")
        
        # Load demo sequence if requested (after UI is initialized)
        if args.demo:
            demo_path = os.path.join(os.path.dirname(__file__), 
                                   'demo_sequences', 'beam_setup_demo.json')
            if os.path.exists(demo_path):
                print(f"📄 Loading demo sequence: {demo_path}")
                try:
                    sequence_data = main_window.file_manager.load_sequence(demo_path, show_dialog=False)
                    if sequence_data:
                        main_window.sequence_editor.load_sequence(sequence_data)
                        print("✅ Demo sequence loaded successfully")
                        print("🎯 Ready to execute demo - click the green 'Run' button!")
                    else:
                        print("❌ Failed to load demo sequence")
                except Exception as e:
                    print(f"❌ Error loading demo sequence: {e}")
            else:
                print("❌ Demo sequence file not found")
        
        # Load specific sequence file if requested (after UI is initialized)
        elif args.load:
            if os.path.exists(args.load):
                print(f"📄 Loading sequence: {args.load}")
                try:
                    sequence_data = main_window.file_manager.load_sequence(args.load, show_dialog=False)
                    if sequence_data:
                        main_window.sequence_editor.load_sequence(sequence_data)
                        print("✅ Sequence loaded successfully")
                        print("🎯 Ready for sequence execution")
                    else:
                        print("❌ Failed to load sequence")
                except Exception as e:
                    print(f"❌ Error loading sequence: {e}")
            else:
                print(f"❌ Sequence file not found: {args.load}")
        else:
            print("🎯 Ready for sequence creation and execution")
        
        # Start the event loop (app and window already initialized)
        return app.app.exec_()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have activated the virtual environment and installed dependencies:")
        print("  source venv/bin/activate")
        print("  pip install pyqt5 pytest pyyaml")
        return 1
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 