# Demo Sequences for CERN Sequencer

This directory contains a comprehensive collection of example sequences demonstrating various aspects of the CERN Sequencer application. Each sequence is properly validated and showcases different use cases and file formats.

## Available Sequences

### 1. `beam_setup_demo.json`
**Format**: JSON  
**Category**: Demo  
**Description**: Basic beam setup operations for CERN accelerator control  
**Steps**: 11 steps  
**Features**:
- Basic beam energy configuration (7 TeV)
- Magnet current settings
- RF frequency configuration
- Event waiting and system diagnostics
- Proper parameter validation

### 2. `particle_physics_experiment.yaml`
**Format**: YAML  
**Category**: Physics  
**Description**: Complete sequence for high-energy particle collision experiment  
**Steps**: 12 steps  
**Features**:
- 13 TeV collision energy setup
- Detector high voltage configuration
- Magnetic field setup (3.8 T)
- Luminosity target settings
- Collision quality monitoring

### 3. `maintenance_sequence.json`
**Format**: JSON  
**Category**: Maintenance  
**Description**: Routine maintenance and diagnostic checks for accelerator components  
**Steps**: 12 steps  
**Features**:
- Safety mode activation
- System cooldown procedures
- Temperature and vacuum integrity checks
- RF system testing
- Comprehensive health monitoring

### 4. `calibration_sequence.yml`
**Format**: YML  
**Category**: Calibration  
**Description**: Precision calibration procedure for detector systems  
**Steps**: 15 steps  
**Features**:
- Environmental temperature control
- Reference voltage calibration
- Precision measurements with high accuracy
- Calibration constant calculation
- Verification procedures

### 5. `simple_test_sequence.json`
**Format**: JSON  
**Category**: Testing  
**Description**: Basic test sequence for validating sequencer functionality  
**Steps**: 6 steps  
**Features**:
- Simple parameter setting
- Basic delay operations
- Event waiting
- Diagnostic execution
- Ideal for testing and learning

### 6. `complex_operations.json`
**Format**: JSON  
**Category**: Operations  
**Description**: Advanced operational sequence demonstrating complex accelerator procedures  
**Steps**: 17 steps  
**Features**:
- Dual beam energy configuration (6.5 TeV each)
- Crossing angle optimization
- Beta* optics configuration
- Bunch intensity control
- Luminosity optimization
- Advanced collision setup

## File Format Support

The sequencer supports three file formats:

- **JSON** (`.json`) - JavaScript Object Notation
- **YAML** (`.yaml`) - YAML Ain't Markup Language
- **YML** (`.yml`) - YAML with shorter extension

## Step Types Demonstrated

All sequences showcase the five supported step types:

1. **LogMessage** - Information logging and status messages
2. **SetParameter** - Setting system parameters with values and units
3. **Delay** - Time delays with configurable precision
4. **WaitForEvent** - Waiting for system events with timeouts
5. **RunDiagnostic** - Executing diagnostic procedures with parameters

## Parameter Validation

All sequences include:
- Proper parameter names and data types
- Numeric values as numbers (not strings)
- Appropriate timeout and retry settings
- Realistic physical units and values
- Complete metadata with versioning

## Usage Instructions

### Loading Demo Sequences

1. **Using Command Line**:
   ```bash
   python run_sequencer.py --demo  # Loads beam_setup_demo.json
   python run_sequencer.py --load demo_sequences/particle_physics_experiment.yaml
   ```

2. **Using Application Menu**:
   - Open CERN Sequencer application
   - Use File → Open (Ctrl+O)
   - Navigate to `demo_sequences/` directory
   - Select desired sequence file

### Testing Sequences

All sequences are designed to work with the mock accelerator control system:
- Parameters are validated but not sent to real hardware
- Events are simulated with realistic timing
- Diagnostics return mock results
- Safe for testing and demonstration

## Sequence Complexity Levels

- **Beginner**: `simple_test_sequence.json`
- **Intermediate**: `beam_setup_demo.json`, `maintenance_sequence.json`
- **Advanced**: `particle_physics_experiment.yaml`, `calibration_sequence.yml`
- **Expert**: `complex_operations.json`

## Customization

These sequences can be used as templates for creating custom sequences:
1. Copy an existing sequence file
2. Modify the metadata (name, description, author)
3. Adjust steps, parameters, and timeouts as needed
4. Save with a new filename
5. Load and test in the application

## Troubleshooting

If you encounter validation errors:
1. Check parameter names match expected values
2. Ensure numeric values are not quoted strings
3. Verify required parameters are present for each step type
4. Check timeout values are positive numbers
5. Validate retry counts are non-negative integers

## Support

For questions about these demo sequences or creating custom sequences:
- Review the main README.md for application usage
- Check the sequence data model documentation
- Refer to step widget implementations for parameter requirements 