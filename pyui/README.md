# PyUI Framework

PyUI is a Python-based UI framework built on top of PyQt5, specifically designed for CERN's particle accelerator control applications. It provides a foundation for creating modern, professional GUI applications with accelerator-specific components and CERN branding.

## Features

- **ApplicationBase**: Base class for PyUI applications with common setup and initialization
- **Widget Registry**: Dynamic widget registration and retrieval system
- **CERN Theming**: Professional blue color scheme and styling
- **StyledButton**: Custom button widget with accent colors and sizing presets
- **High DPI Support**: Automatic scaling for high-resolution displays
- **Extensible Architecture**: Easy to add new widgets and components

## Quick Start

### Hello World Example

The simplest way to get started with PyUI is with our Hello World example:

```python
#!/usr/bin/env python3
"""PyUI Hello World Example"""

import sys
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel
from pyui.pyui import ApplicationBase, get_widget

class HelloWorldWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyUI Hello World")
        self.setMinimumSize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Hello, PyUI Framework!")
        title.setStyleSheet("color: #0066CC; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Get PyUI StyledButton
        StyledButton = get_widget("StyledButton")
        if StyledButton:
            hello_btn = StyledButton("Say Hello")
            hello_btn.clicked.connect(lambda: print("Hello from PyUI!"))
            layout.addWidget(hello_btn)

class HelloWorldApp(ApplicationBase):
    def __init__(self):
        super().__init__(app_name="PyUI Hello World", app_version="1.0.0")
        
    def create_main_window(self):
        self.main_window = HelloWorldWindow()
        return self.main_window

if __name__ == "__main__":
    app = HelloWorldApp()
    sys.exit(app.run())
```

### Running the Hello World Example

```bash
# From the pyui directory
python hello_world_example.py
```

## Installation & Setup

### Prerequisites

- Python 3.7+
- PyQt5
- pytest (for testing)

### Installation

```bash
# Install required dependencies
pip install pyqt5 pytest

# Clone or download the PyUI framework
# No additional installation required - import directly
```

## Core Components

### ApplicationBase

The foundation of all PyUI applications. Provides:

- PyQt application initialization
- High DPI scaling support
- CERN branding and window setup
- Consistent application structure

```python
from pyui.pyui import ApplicationBase

class MyApp(ApplicationBase):
    def __init__(self):
        super().__init__(
            app_name="My CERN Application",
            app_version="1.0.0"
        )
    
    def create_main_window(self):
        # Create your main window here
        pass
    
    def setup_ui(self):
        # Optional UI setup
        pass
```

### Widget Registry

PyUI includes a widget registry system for managing custom components:

```python
from pyui.pyui import register_widget, get_widget, list_widgets

# Register a custom widget
register_widget("MyWidget", MyCustomWidget)

# Get a widget from the registry
MyWidget = get_widget("MyWidget")

# List all available widgets
widgets = list_widgets()
print(f"Available widgets: {widgets}")
```

### StyledButton

A custom button widget with CERN theming:

```python
from pyui.pyui import get_widget

StyledButton = get_widget("StyledButton")
if StyledButton:
    # Create a button
    btn = StyledButton("Click Me")
    
    # Set accent color
    btn.set_accent_color("#00AA00")  # Green
    
    # Set size preset
    btn.set_size("large")  # small, medium, large
    
    # Connect to handler
    btn.clicked.connect(my_handler)
    
    # Handle double-click
    btn.double_clicked.connect(my_double_click_handler)
```

## Examples

### Basic Application

```python
from pyui.pyui import ApplicationBase
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My PyUI App")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.addWidget(QLabel("Welcome to PyUI!"))

class MyApp(ApplicationBase):
    def __init__(self):
        super().__init__(app_name="My App", app_version="1.0.0")
    
    def create_main_window(self):
        return MyMainWindow()

if __name__ == "__main__":
    app = MyApp()
    app.run()
```

### Using Multiple Widgets

```python
from pyui.pyui import ApplicationBase, get_widget
from PyQt5.QtWidgets import QVBoxLayout, QWidget

class MultiWidgetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        StyledButton = get_widget("StyledButton")
        if StyledButton:
            # Create multiple buttons with different styles
            btn1 = StyledButton("Primary Action")
            btn1.set_accent_color("#0066CC")  # Blue
            
            btn2 = StyledButton("Secondary Action")
            btn2.set_accent_color("#CC6600")  # Orange
            btn2.set_size("small")
            
            btn3 = StyledButton("Danger Action")
            btn3.set_accent_color("#CC0000")  # Red
            btn3.set_size("large")
            
            layout.addWidget(btn1)
            layout.addWidget(btn2)
            layout.addWidget(btn3)
```

## API Reference

### ApplicationBase

**Constructor:**
- `__init__(self, app_name="PyUI Application", app_version="1.0.0")`

**Methods:**
- `initialize_application()`: Initialize the PyQt application
- `create_main_window(window_class=None)`: Create the main window (override required)
- `setup_ui()`: Setup UI components (optional override)
- `run()`: Run the application event loop
- `quit()`: Quit the application

### Widget Registry Functions

- `register_widget(name, widget_class)`: Register a widget class
- `get_widget(name)`: Get a widget class by name
- `list_widgets()`: List all registered widget names

### StyledButton

**Constructor:**
- `__init__(self, text="", parent=None)`

**Methods:**
- `set_accent_color(color)`: Set button accent color (hex string)
- `set_size(size)`: Set button size ("small", "medium", "large")

**Signals:**
- `clicked`: Standard button click
- `double_clicked`: Double-click event

## Testing

PyUI includes comprehensive unit tests:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_application_base.py
pytest tests/test_example_widget.py

# Run with verbose output
pytest tests/ -v
```

## Examples Directory

The PyUI framework includes several example applications:

1. **hello_world_example.py**: Minimal PyUI application demonstrating basic usage
2. **example_app.py**: More comprehensive example showing multiple widgets and features

```bash
# Run the Hello World example
python hello_world_example.py

# Run the comprehensive example
python example_app.py
```

## Architecture

PyUI follows a modular architecture:

```
pyui/
├── pyui/
│   ├── __init__.py              # Package initialization and widget registry
│   ├── application_base.py      # Base application class
│   ├── widgets/
│   │   ├── __init__.py         # Widget package initialization
│   │   └── example_widget.py   # StyledButton implementation
│   ├── layouts/
│   │   └── __init__.py         # Layout utilities (future)
│   └── utils/
│       └── __init__.py         # Utility functions (future)
├── hello_world_example.py       # Hello World example
├── example_app.py               # Comprehensive example
└── README.md                   # This file
```

## Future Enhancements

Planned features for future releases:

- **Layout Managers**: Specialized layouts for accelerator control interfaces
- **Data Widgets**: Widgets for displaying sensor data, graphs, and measurements
- **Control Widgets**: Specialized controls for accelerator parameters
- **Theming System**: Customizable themes beyond the default CERN theme
- **Plugin System**: Dynamic loading of custom widgets and components
- **Configuration Management**: Settings and preferences handling
- **Internationalization**: Multi-language support

## Contributing

PyUI is designed to be extensible. To add new widgets:

1. Create your widget class inheriting from appropriate PyQt widget
2. Register it using `register_widget()`
3. Add unit tests in the `tests/` directory
4. Update documentation and examples

## Requirements

- Python 3.7+
- PyQt5
- pytest (for testing)

## License

This project is developed for CERN's particle accelerator control systems.

## Support

For questions, issues, or contributions related to PyUI, please contact the development team or refer to the project documentation.

---

*PyUI Framework - Empowering CERN's Accelerator Control Applications* 