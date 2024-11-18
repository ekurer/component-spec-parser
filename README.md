# Component Specification Parser

A Python system that parses component datasheets and determines compatibility based on operating voltage and temperature ranges.

## Project Structure
- `component_parser.py` - Main parser implementation
- `test_component_parser.py` - Test suite
- `Task example files/` - Sample datasheet files for testing the parser
  - Contains text-extracted datasheets from various electronic components
  - Used to verify parser accuracy with real-world examples
  - Each file contains voltage and temperature specifications in different formats

## Requirements
- Python 3.x (no additional packages required)

## Usage
```bash
python component_parser.py [-v]  # -v for verbose output
```

When prompted, enter:
- Operating voltage (V)
- Operating temperature (°C)

The program will display all compatible components.

## Running Tests
```bash
python test_component_parser.py
```

## How It Works
1. Reads component datasheet files (.txt)
2. Uses regular expressions to parse:
   - Voltage ranges (e.g., "3.15V to 3.45V Operation")
   - Temperature ranges (e.g., "-40°C to +85°C")
3. For multiple ranges in a file:
   - Uses the range if all are identical
   - Sets to None if ranges differ
4. A component is compatible if both voltage and temperature are within range

## Implementation Details
- Regular expressions handle various text formats:
  - Direct ranges: "3.15V to 3.45V"
  - Prefixed ranges: "Supply voltage: 2.7V to 5.5V"
  - Suffixed ranges: "3.15V to 3.45V Operation"
- Handles both Latin-1 and UTF-8 encodings
- Validates ranges for reasonable values
- Comprehensive test coverage with unittest

## Assumptions
- Voltage specifications contain 'V' or 'v' unit
- Temperature specifications in Celsius (°C, C)
- When multiple ranges exist, they must be identical to be valid
- Voltage and temperature ranges are within reasonable bounds for electronic components