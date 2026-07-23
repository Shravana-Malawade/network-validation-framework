# Python Learning Notes

## Session 1 - YAML Configuration

### Topics Learned
- Reading YAML files using the `yaml` library.
- Using `yaml.safe_load()` to convert YAML into a Python dictionary.
- Nested dictionaries.
- Accessing dictionary values using keys.
- Writing reusable functions.
- Returning values from functions.
- File handling using `with open()`.

### Python Concepts
- Variables
- Strings
- Dictionaries
- Functions
- Parameters
- Return statements
- Imports

---

## Session 2 - Python Logging

### Topics Learned
- Python built-in `logging` module.
- Creating a Logger object.
- Creating a FileHandler object.
- Creating a Formatter object.
- Setting log levels.
- Connecting Logger → FileHandler → Formatter.
- Returning the Logger object to `main.py`.

### Python Concepts
- Objects
- Methods
- Standard Library
- Built-in function `getattr()`
- Nested dictionaries
- Conditional statements (`if`)
- Lists (`logger.handlers`)
- Function parameters
- Return values

### Logging Flow

config.yaml
↓
config_loader.py
↓
Dictionary
↓
logger.py
↓
Logger Object
↓
FileHandler
↓
Formatter
↓
framework.log

### Key Learnings
- Logger decides what should be logged.
- FileHandler decides where logs are stored.
- Formatter decides how log messages look.
- Configuration should come from YAML instead of hardcoding values.
- Every module should have a single responsibility.
