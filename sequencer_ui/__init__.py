"""
Sequencer UI Package

Contains the main Sequencer UI application for editing and executing 
operational sequences within CERN's particle accelerator control domain.
"""

from .sequencer_app import SequencerApp, SequencerMainWindow

__version__ = "0.1.0"
__all__ = ["SequencerApp", "SequencerMainWindow"]
