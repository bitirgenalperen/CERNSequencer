# Visual Testing Checklist - CERN Sequencer MVP (Post-Milestone 3)

## Prerequisites

- [X] Virtual environment is activated (`source venv/bin/activate`)
- [X] Dependencies are installed (`pip install pyqt5 pytest pyyaml`)
- [X] All tests pass (`python -m pytest tests/ -v`)

## Application Launch

- [ ] **Method 1**: `python run_sequencer.py` - launches without errors
- [ ] **Method 2**: `python run_sequencer.py --demo` - launches with demo sequence loaded
- [ ] **Method 3**: `python run_sequencer.py --load file.json` - launches with specific file
- [ ] Application window opens with CERN Sequencer UI title
- [ ] No critical error messages in terminal (warnings are OK)
- [ ] Enhanced startup messages with emoji indicators and status feedback

## 1. Main Interface Layout Verification

- [ ] **Window**: Minimum size 1200x800, resizable with professional CERN branding
- [ ] **Top Menu Bar**: File, Sequence, Help menus with new Pause/Resume actions
- [ ] **Toolbar**: New, Open, Save, Example, Validate, Run, Stop buttons with color coding
- [ ] **Main Content Area (75%)**: Horizontal splitter with Sequence Editor and Properties
  - [ ] **Left Panel (70%)**: Sequence Editor with step list area and drag-and-drop
  - [ ] **Right Panel (30%)**: Properties panel shows "Sequence Properties" header
- [ ] **Execution Status Panel (25%)**: Bottom panel with vertical splitter showing:
  - [ ] Progress bar with percentage and step counts
  - [ ] Current execution status with color-coded indicators
  - [ ] Current step display with descriptions
  - [ ] Execution statistics (Total/Success/Failed counters)
  - [ ] Pause/Resume control buttons
- [ ] **Status Bar**: Shows "Ready - Create a new sequence..." message
- [ ] **Splitters**: Can drag between panels to resize (horizontal and vertical)

## 2. New Sequence Creation

- [ ] Click "New" button → creates new sequence
- [ ] File → New Sequence (Ctrl+N) → creates new sequence
- [ ] Window title shows "CERN Sequencer UI - Untitled Sequence"
- [ ] Left panel shows empty step list
- [ ] Right panel shows sequence properties with default metadata
- [ ] Status bar shows "New sequence created"

## 3. Step Management

### Adding Steps

- [ ] **Dropdown Method**: Use dropdown in sequence editor to add steps
- [ ] **Menu Method**: Sequence → Add Step → [Step Type]
- [ ] **Available Step Types**: SetParameter, WaitForEvent, Delay, RunDiagnostic, LogMessage
- [ ] Each added step appears in the step list with proper icon/description
- [ ] Status bar confirms step addition ("Added [Step Type] step")

### Step Types Configuration

- [ ] **Set Parameter Step**:
  - [ ] Parameter name field (text input)
  - [ ] Parameter value field (number/text input)
  - [ ] Description field
  - [ ] Real-time parameter validation
  
- [ ] **Wait for Event Step**:
  - [ ] Event name field
  - [ ] Timeout field (numeric, in seconds)
  - [ ] Event source dropdown
  - [ ] Match criteria options
  
- [ ] **Delay Step**:
  - [ ] Duration field (numeric, in seconds)
  - [ ] Description field
  - [ ] Validation for positive numbers
  
- [ ] **Run Diagnostic Step**:
  - [ ] Diagnostic name field
  - [ ] Parameters table (add/remove rows)
  - [ ] Timeout configuration
  - [ ] Continue on failure checkbox
  
- [ ] **Log Message Step**:
  - [ ] Message text area
  - [ ] Log level dropdown (INFO, WARNING, ERROR, DEBUG)
  - [ ] Category selection
  - [ ] Timestamp options

### Step Interaction
- [ ] **Selection**: Click step → properties panel updates with step details
- [ ] **Editing**: Modify parameters → changes reflected in properties panel
- [ ] **Real-time Updates**: Parameter changes update step display immediately
- [ ] **Validation**: Invalid parameters show error indicators

### Step Reordering
- [ ] **Drag & Drop**: Can drag steps up/down in list
- [ ] **Visual Feedback**: Drag operation shows insertion point
- [ ] **Completion**: Drop updates step order correctly
- [ ] **Properties Update**: Reordered sequence maintains step selection

### Step Removal
- [ ] **Context Menu**: Right-click step → Remove option
- [ ] **Confirmation**: Shows "Are you sure?" dialog
- [ ] **Deletion**: Confirms removal and updates display
- [ ] **Selection Update**: Clears selection if removed step was selected

## 4. Demo Sequences Testing

### Main Demo Sequence (beam_setup_demo.json)
- [ ] Click "Example" button → loads beam setup demo sequence
- [ ] File → Load Example Sequence → loads beam setup demo sequence
- [ ] **Sequence Contains 11 Steps**:
  - [ ] Step 1: Log Message (Initialize beam setup procedure)
  - [ ] Step 2: Set Parameter (beam_energy = 7000.0 GeV)
  - [ ] Step 3: Delay (3.0 seconds for stabilization)
  - [ ] Step 4: Wait for Event (beam_stable_signal, 10s timeout)
  - [ ] Step 5: Set Parameter (magnet_current_Q1 = 150.0 A)
  - [ ] Step 6: Run Diagnostic (beam_position_check)
  - [ ] Step 7: Set Parameter (rf_frequency = 400.789 MHz)
  - [ ] Step 8: Delay (2.0 seconds for RF lock)
  - [ ] Step 9: Wait for Event (rf_lock_signal, 8s timeout)
  - [ ] Step 10: Run Diagnostic (full_system_check)
  - [ ] Step 11: Log Message (Complete beam setup procedure)
- [ ] Window title shows "CERN Sequencer UI - Beam Setup Demo Sequence"
- [ ] Properties panel shows sequence metadata with realistic CERN values
- [ ] Status bar shows "Demo sequence loaded"

### Additional Demo Sequences
- [ ] **Demo Sequences Directory**: `demo_sequences/` contains multiple examples
- [ ] **Multiple Formats**: JSON, YAML, and YML files available
- [ ] **Load Different Demos**: Can load particle_physics_experiment.yaml, maintenance_sequence.json, etc.
- [ ] **Validation**: All demo sequences load without validation errors
- [ ] **Realistic Parameters**: Sequences contain actual CERN operation values

## 5. File Operations

### Save Functionality
- [ ] **Save New Sequence**:
  - [ ] File → Save Sequence (Ctrl+S) → opens Save dialog
  - [ ] Can choose JSON or YAML format
  - [ ] File saves successfully
  - [ ] Window title updates with filename
  - [ ] Status bar shows "Saved sequence to [filename]"
  
- [ ] **Save As**:
  - [ ] File → Save Sequence As (Ctrl+Shift+S) → opens Save As dialog
  - [ ] Can save with new name/location
  - [ ] Updates current file reference
  
- [ ] **Save Existing**:
  - [ ] Modify sequence → window title shows asterisk (*)
  - [ ] Ctrl+S saves to current file without dialog
  - [ ] Asterisk disappears after save

### Load Functionality
- [ ] **Open Sequence**:
  - [ ] File → Open Sequence (Ctrl+O) → opens file dialog
  - [ ] Can filter by JSON/YAML files
  - [ ] Successfully loads sequence data
  - [ ] All steps appear correctly configured
  - [ ] Properties panel shows loaded metadata
  
- [ ] **Unsaved Changes Protection**:
  - [ ] Modify sequence → try to open new file
  - [ ] Shows "Unsaved changes" confirmation dialog
  - [ ] "Yes" continues, "No" cancels operation

### Recent Files
- [ ] **Menu Population**:
  - [ ] File → Recent Files shows recently opened files
  - [ ] Files appear with just filename (not full path)
  - [ ] Maximum 10 recent files shown
  
- [ ] **Recent File Opening**:
  - [ ] Click recent file → loads sequence immediately
  - [ ] Updates recent files order (most recent first)
  - [ ] Shows unsaved changes dialog if needed
  
- [ ] **Clear Recent Files**:
  - [ ] File → Recent Files → Clear Recent Files
  - [ ] Menu shows "No recent files" after clearing

### Export Functionality
- [ ] **Export as JSON**:
  - [ ] File → Export → Export as JSON
  - [ ] Opens save dialog with JSON filter
  - [ ] Creates valid JSON file
  - [ ] Status bar confirms export
  
- [ ] **Export as YAML**:
  - [ ] File → Export → Export as YAML
  - [ ] Opens save dialog with YAML filter
  - [ ] Creates valid YAML file (if PyYAML installed)
  - [ ] Shows warning if PyYAML not available

## 6. Sequence Execution Testing

### Basic Execution Controls
- [ ] **Run Button (F5)**: Green button starts sequence execution
- [ ] **Stop Button (F6)**: Red button stops running sequence
- [ ] **Pause Button (Ctrl+P)**: Orange button pauses execution mid-sequence
- [ ] **Resume Button (Ctrl+R)**: Green button resumes paused execution
- [ ] **Button States**: Buttons enable/disable appropriately based on execution state

### Execution Status Panel
- [ ] **Progress Bar**: Shows percentage completion and step counts (e.g., "45% (5/11 steps)")
- [ ] **Status Indicator**: Color-coded status display
  - [ ] 🟢 Green: RUNNING, COMPLETED, Ready states
  - [ ] 🔴 Red: STOPPED, FAILED states
  - [ ] 🟠 Orange: PAUSED state
  - [ ] 🔵 Blue: Ready/Idle state
- [ ] **Current Step**: Shows description of currently executing step (truncated if long)
- [ ] **Execution Statistics**: Live counters for Total/Success/Failed steps
- [ ] **Real-time Updates**: All displays update during execution

### Execution Flow Testing
- [ ] **Normal Execution**: Load demo sequence → Run → observe complete execution
- [ ] **Step-by-Step Progress**: Each step updates status panel during execution
- [ ] **Realistic Timing**: Steps execute with appropriate delays (mock interface simulation)
- [ ] **Completion Handling**: Sequence completes successfully with final status update
- [ ] **Error Simulation**: Some steps may fail (mock interface 85% success rate)

### Execution Control Testing
- [ ] **Mid-Execution Pause**: Start sequence → Pause during execution → status shows PAUSED
- [ ] **Resume from Pause**: Paused sequence → Resume → execution continues from current step
- [ ] **Stop During Execution**: Running sequence → Stop → execution terminates immediately
- [ ] **UI Responsiveness**: Interface remains responsive during execution (non-blocking threading)

### Menu Integration
- [ ] **Sequence Menu**: Pause and Resume actions appear in Sequence menu
- [ ] **Keyboard Shortcuts**: F5 (Run), F6 (Stop), Ctrl+P (Pause), Ctrl+R (Resume) work correctly
- [ ] **Menu State Updates**: Menu items enable/disable based on execution state

### Mock Interface Integration
- [ ] **Parameter Setting**: SetParameter steps show realistic simulation messages
- [ ] **Event Waiting**: WaitForEvent steps show timeout behavior and random success
- [ ] **Delays**: Delay steps execute with precise timing
- [ ] **Diagnostics**: RunDiagnostic steps show pass/fail results with realistic timing
- [ ] **Logging**: LogMessage steps appear in console with proper formatting

## 7. Validation System

- [ ] **Manual Validation**:
  - [ ] Click "Validate" button → shows validation dialog
  - [ ] Sequence → Validate Sequence (F7) → shows validation dialog
  - [ ] Valid sequence shows "Sequence is valid!" message
  
- [ ] **Invalid Sequence Testing**:
  - [ ] Create step with missing required parameters
  - [ ] Validation shows specific error messages
  - [ ] Lists all validation errors found
  
- [ ] **Auto-validation**:
  - [ ] Properties panel shows validation status
  - [ ] "✓ Valid" or "✗ Invalid" indicator
  - [ ] Error list appears for invalid sequences

## 8. User Interface Polish

### Visual Design
- [ ] **CERN Branding**: Blue accent colors (#0066CC) used consistently throughout
- [ ] **Professional Layout**: Clean, organized interface with proper spacing and alignment
- [ ] **Color-Coded Controls**: Green (Run/Resume), Red (Stop), Orange (Pause) button styling
- [ ] **Icons/Styling**: Buttons have appropriate styling, hover effects, and visual feedback
- [ ] **Typography**: Readable fonts with appropriate hierarchy and sizes
- [ ] **Execution Status Panel**: Professional design matching main interface theme

### User Experience
- [ ] **Tooltips**: All buttons show helpful tooltips on hover
- [ ] **Comprehensive Keyboard Shortcuts**: 
  - [ ] Ctrl+N (New), Ctrl+O (Open), Ctrl+S (Save), Ctrl+Shift+S (Save As)
  - [ ] F5 (Run), F6 (Stop), Ctrl+P (Pause), Ctrl+R (Resume)
  - [ ] F7 (Validate), Ctrl+Q (Quit)
- [ ] **Status Feedback**: Status bar and execution panel update for all operations
- [ ] **Progress Indication**: Real-time feedback for execution and file operations
- [ ] **Professional Startup**: Enhanced run script with command-line options and feedback

### Responsiveness
- [ ] **Window Resizing**: Interface adapts to different window sizes (minimum 1200x800)
- [ ] **Panel Sizing**: Horizontal (70%/30%) and vertical (75%/25%) panel ratios maintained
- [ ] **Splitter Dragging**: Can adjust panel sizes smoothly in both directions
- [ ] **Scroll Areas**: Long step lists and execution logs scroll properly
- [ ] **Real-time Updates**: Execution status updates don't block UI interaction

## 9. Error Handling

### File Operations
- [ ] **Non-existent File**: Loading missing file shows user-friendly error dialog
- [ ] **Corrupted File**: Loading invalid JSON/YAML shows descriptive error dialog
- [ ] **Permission Errors**: Write-protected location shows appropriate error message
- [ ] **Disk Full**: Saving when disk full shows meaningful error with guidance

### Data Validation
- [ ] **Invalid Parameters**: Shows validation errors without crashing application
- [ ] **Empty Required Fields**: Prevents saving with missing data and clear feedback
- [ ] **Type Mismatches**: Handles incorrect data types gracefully with user guidance
- [ ] **Sequence Validation**: Invalid sequences show specific error details

### Execution Error Handling
- [ ] **Empty Sequence**: Attempting to run empty sequence shows appropriate warning
- [ ] **Invalid Sequence**: Running invalid sequence shows validation errors first
- [ ] **Execution Failures**: Mock interface failures show user-friendly error messages
- [ ] **Timeout Handling**: Event timeouts display clear timeout messages
- [ ] **Interrupted Execution**: Stopping mid-execution handles cleanup properly

### Application Stability
- [ ] **No Crashes**: Application remains stable during all operations including execution
- [ ] **Memory Leaks**: Extended use and multiple executions don't degrade performance
- [ ] **Thread Safety**: Execution threading doesn't cause UI freezing or crashes
- [ ] **Clean Shutdown**: Application closes cleanly with File → Exit or window close

## 10. Advanced Features

### Backup System
- [ ] **Automatic Backups**: Saving existing file creates timestamped backup
- [ ] **Backup Cleanup**: Old backups are automatically removed (keeps last 5)
- [ ] **Backup Location**: Backups created in same directory as original file

### Settings Persistence
- [ ] **Recent Files**: Recent files list persists between application runs
- [ ] **Window State**: Window size/position remembered across sessions
- [ ] **User Preferences**: Settings stored in system-appropriate location using QSettings

### Enhanced Command-Line Interface
- [ ] **Demo Mode**: `python run_sequencer.py --demo` loads demo sequence automatically
- [ ] **File Loading**: `python run_sequencer.py --load filename` loads specific sequence
- [ ] **Help System**: `python run_sequencer.py --help` shows usage information
- [ ] **Error Handling**: Invalid command-line arguments show helpful error messages

### Multi-Format Support
- [ ] **JSON Format**: Complete JSON serialization/deserialization support
- [ ] **YAML Format**: YAML support when PyYAML is available
- [ ] **Format Detection**: Automatic format detection based on file extension
- [ ] **Cross-Format Compatibility**: Can export JSON sequences as YAML and vice versa

## 11. Integration Testing

### Component Integration
- [ ] **Sequence Editor ↔ File Manager**: Save/load updates editor correctly
- [ ] **Sequence Editor ↔ Properties Panel**: Selection updates properties panel
- [ ] **File Manager ↔ Recent Files**: File operations update recent files menu
- [ ] **Step Widgets ↔ Data Model**: Parameter changes persist correctly
- [ ] **Sequence Executor ↔ UI**: Execution updates status panel in real-time
- [ ] **Sequence Executor ↔ Mock Interface**: All step types execute correctly

### Signal Flow Integration
- [ ] **sequence_changed**: Emitted when sequence modified, updates window title
- [ ] **sequence_loaded**: Emitted when sequence loaded from file
- [ ] **step_selected**: Emitted when step selection changes
- [ ] **Window Title Updates**: Reflects current file and modification state correctly

### Execution Integration
- [ ] **Execution Signals**: 12 executor signals update UI components correctly
- [ ] **Progress Updates**: Real-time progress updates during execution
- [ ] **Status Synchronization**: UI state matches execution state consistently
- [ ] **Thread Safety**: No race conditions between execution thread and UI thread
- [ ] **Control Integration**: UI controls properly manage executor state

### Full Workflow Testing
- [ ] **Complete Cycle**: Create → Edit → Save → Load → Execute → Monitor
- [ ] **Error Recovery**: Application handles errors gracefully throughout workflow
- [ ] **State Persistence**: Application state maintained correctly across operations
- [ ] **User Experience**: Smooth transitions between different application modes

## 12. Completion Checklist

### Core Functionality
- [ ] All basic functionality working correctly (create, edit, save, load)
- [ ] File operations (save/load/export) functional in multiple formats
- [ ] Step management (add/edit/remove/reorder) working with drag-and-drop
- [ ] Validation system operational with real-time feedback
- [ ] Error handling graceful and user-friendly throughout application

### Execution System
- [ ] Sequence execution working with real-time status updates
- [ ] All execution controls functional (run/stop/pause/resume)
- [ ] Mock accelerator interface integration working correctly
- [ ] Execution status panel displaying comprehensive information
- [ ] Threading and UI responsiveness maintained during execution

### User Interface & Experience
- [ ] UI polish and responsiveness satisfactory with 1200x800 minimum size
- [ ] Professional CERN branding and color-coded controls
- [ ] All keyboard shortcuts working correctly
- [ ] Command-line interface functional with demo and file loading options
- [ ] Demo sequences load and execute without errors

### Quality Assurance
- [ ] No critical bugs or crashes found during comprehensive testing
- [ ] Memory usage stable during extended use and multiple executions
- [ ] All 133 automated tests passing
- [ ] Cross-platform compatibility verified (if testing on multiple platforms)

## Issues Found

_Use this section to note any issues discovered during testing:_

- [ ] Issue 1: [Description]
- [ ] Issue 2: [Description]
- [ ] Issue 3: [Description]

---

**Testing Notes**: 
- Test on different screen sizes/resolutions (minimum 1200x800 required)
- Try both JSON and YAML formats with multiple demo sequences
- Test execution with sequences of different sizes and complexity levels
- Verify memory usage doesn't grow excessively during multiple execution cycles
- Test command-line options: `--demo`, `--load filename`, `--help`
- Verify all keyboard shortcuts work: F5, F6, Ctrl+P, Ctrl+R, Ctrl+N, Ctrl+O, Ctrl+S
- Test execution interruption (pause/resume/stop) at different sequence points
- Verify UI responsiveness during long-running sequences 