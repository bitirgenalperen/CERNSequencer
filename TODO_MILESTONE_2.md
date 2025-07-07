# TODO: Milestone 2 Visual Testing Checklist

## Prerequisites

- [X] Virtual environment is activated (`source venv/bin/activate`)
- [X] Dependencies are installed (`pip install pyqt5 pytest pyyaml`)
- [X] All tests pass (`python -m pytest tests/ -v`)

## Application Launch

- [X] **Method 1**: `python run_sequencer.py` - launches without errors
- [X] Application window opens with CERN Sequencer UI title
- [X] No critical error messages in terminal (warnings are OK)

## 1. Main Interface Layout Verification

- [X] **Left Panel (70%)**: Sequence Editor is visible with step list area
- [X] **Right Panel (30%)**: Properties panel shows "Sequence Properties" header
- [X] **Top Menu Bar**: File, Sequence, Help menus are present
- [X] **Toolbar**: New, Open, Save, Example, Validate, Run, Stop buttons visible
- [X] **Status Bar**: Shows "Ready - Create a new sequence..." message
- [X] **Window**: Minimum size 1000x700, resizable
- [X] **Splitter**: Can drag between left/right panels to resize

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

## 4. Example Sequence Testing

- [ ] Click "Example" button → loads example sequence
- [ ] File → Load Example Sequence → loads example sequence
- [ ] **Sequence Contains 6 Steps**:
  - [ ] Step 1: Set Parameter (Magnet_Current_A = 100.5)
  - [ ] Step 2: Delay (2.0 seconds)
  - [ ] Step 3: Set Parameter (RF_Frequency_B = 400.12)
  - [ ] Step 4: Wait for Event (Beam_Ready_Signal, 10s timeout)
  - [ ] Step 5: Run Diagnostic (Beam_Position_Check)
  - [ ] Step 6: Log Message (completion message)
- [ ] Window title shows "CERN Sequencer UI - Example Beam Setup Sequence"
- [ ] Properties panel shows sequence metadata (name, description, author, etc.)
- [ ] Status bar shows "Example sequence loaded"

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

## 6. Validation System

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

## 7. User Interface Polish

### Visual Design
- [ ] **CERN Branding**: Blue accent colors (#0066CC) used consistently
- [ ] **Professional Layout**: Clean, organized interface design
- [ ] **Icons/Styling**: Buttons have appropriate styling and hover effects
- [ ] **Typography**: Readable fonts and appropriate sizes

### User Experience
- [ ] **Tooltips**: All buttons show helpful tooltips on hover
- [ ] **Keyboard Shortcuts**: Ctrl+N, Ctrl+O, Ctrl+S, F5, F7 work correctly
- [ ] **Status Feedback**: Status bar updates for all operations
- [ ] **Progress Indication**: Clear feedback for all user actions

### Responsiveness
- [ ] **Window Resizing**: Interface adapts to different window sizes
- [ ] **Panel Sizing**: Left/right panel ratio maintained during resize
- [ ] **Splitter Dragging**: Can adjust panel sizes smoothly
- [ ] **Scroll Areas**: Long step lists scroll properly

## 8. Error Handling

### File Operations
- [ ] **Non-existent File**: Loading missing file shows user-friendly error
- [ ] **Corrupted File**: Loading invalid JSON/YAML shows error dialog
- [ ] **Permission Errors**: Write-protected location shows appropriate error
- [ ] **Disk Full**: Saving when disk full shows meaningful error

### Data Validation
- [ ] **Invalid Parameters**: Shows validation errors without crashing
- [ ] **Empty Required Fields**: Prevents saving with missing data
- [ ] **Type Mismatches**: Handles incorrect data types gracefully

### Application Stability
- [ ] **No Crashes**: Application remains stable during all operations
- [ ] **Memory Leaks**: Extended use doesn't cause performance degradation
- [ ] **Clean Shutdown**: Application closes cleanly with File → Exit

## 9. Advanced Features

### Backup System
- [ ] **Automatic Backups**: Saving existing file creates timestamped backup
- [ ] **Backup Cleanup**: Old backups are automatically removed (keeps last 5)
- [ ] **Backup Location**: Backups created in same directory as original

### Settings Persistence
- [ ] **Recent Files**: Recent files list persists between application runs
- [ ] **Window State**: Window size/position remembered (if implemented)
- [ ] **User Preferences**: Settings stored in system-appropriate location

## 10. Integration Testing

### Component Integration
- [ ] **Sequence Editor ↔ File Manager**: Save/load updates editor correctly
- [ ] **Sequence Editor ↔ Properties Panel**: Selection updates properties
- [ ] **File Manager ↔ Recent Files**: File operations update recent files menu
- [ ] **Step Widgets ↔ Data Model**: Parameter changes persist correctly

### Signal Flow
- [ ] **sequence_changed**: Emitted when sequence modified
- [ ] **sequence_loaded**: Emitted when sequence loaded from file
- [ ] **step_selected**: Emitted when step selection changes
- [ ] **Window Title Updates**: Reflects current file and modification state

## Completion Checklist

- [ ] All basic functionality working correctly
- [ ] File operations (save/load/export) functional
- [ ] Step management (add/edit/remove/reorder) working
- [ ] Validation system operational
- [ ] Error handling graceful and user-friendly
- [ ] UI polish and responsiveness satisfactory
- [ ] No critical bugs or crashes found

## Issues Found

_Use this section to note any issues discovered during testing:_

- [ ] Issue 1: [Description]
- [ ] Issue 2: [Description]
- [ ] Issue 3: [Description]

---

**Testing Notes**: 
- Test on different screen sizes/resolutions if possible
- Try both JSON and YAML formats (if PyYAML available)
- Test with sequences of different sizes (1 step vs 20+ steps)
- Verify memory usage doesn't grow excessively with large sequences 