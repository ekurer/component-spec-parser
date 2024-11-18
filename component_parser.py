#!/usr/bin/env python3

import os
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Test the pattern first with a simpler version
voltage_pattern = re.compile(
    r'(?:'  # Start main group
        r'(?:•\s*)?'  # Optional bullet
        r'(?:'  # Start pattern alternatives
            # Direct voltage range pattern (putting this first)
            r'(?:[-+]?\s*\d+\.?\d*\s*-?[Vv])'  # First number with V
            r'\s*(?:to|[-–]|,)\s*'  # Separator (removed general whitespace option)
            r'(?:[-+]?\s*\d+\.?\d*\s*-?[Vv])'  # Second number with V
            r'(?:\s+(?:Operation|operation))?'  # Optional Operation suffix
            r'|'  # OR
            # Before keywords pattern
            r'(?:(?:v(?:dd|ref|in)?|input|supply|voltage|power)'  # Keywords before
            r'(?:\s+(?:range|voltage))?'  # Optional range/voltage
            r'(?:\s*(?:of|from|:))?)'  # Optional separators
            r'\s*'  # Required space
            r'(?:[-+]?\s*\d+\.?\d*\s*-?[Vv])'  # First number
            r'\s*(?:to|[-–]|,)\s*'  # Separator
            r'(?:[-+]?\s*\d+\.?\d*\s*-?[Vv])'  # Second number
        r')'
        r'(?![.\d])'  # Negative lookahead
    r')',
    re.IGNORECASE | re.DOTALL
)

# Carefully structured temperature pattern with balanced parentheses
temp_pattern = re.compile(
    r'(?:'  # Start main group
        r'(?:•\s*)?'  # Optional bullet
        r'(?:'  # Start pattern alternatives
            # Various temperature formats
            r'(?:'  # Temperature keywords group
                r'(?:temperature|t(?:a|j))'  # Base keywords
                r'(?:\s+(?:grade|range))?'  # Optional grade/range
                r'(?:\s*(?:\d+\s*:|:))?'  # Added standalone colon
                r'|'
                r'(?:industrial\s+temperature)'  # Alternative keyword
                r'|'
                r'(?:operation\s+(?:over|at))'  # Alternative keyword
                r'|'
                r'(?:operating)'  # Simple operating keyword
            r')'
            r'[^.]*?'  # Non-greedy match
            r'(?:[-+]?\s*\d+\.?\d*)'  # First number
            r'(?:\s*°?\s*[Cc])?'  # Optional celsius
            r'(?:\s*(?:to|[-–]|,|\s+))\s*'  # Separator
            r'(?:[-+]?\s*\d+\.?\d*)'  # Second number
            r'(?:\s*°?\s*[Cc])'  # Required celsius at end
        r')'  # End pattern alternatives
        r'(?![.\d])'  # Negative lookahead
    r')',  # End main group
    re.IGNORECASE | re.DOTALL
)

class Component:
    def __init__(self, name):
        self.name = name
        self.voltage_ranges = []
        self.temperature_ranges = []
        self.voltage_range = None
        self.temperature_range = None

    def determine_ranges(self):
        # If ranges are identical, use that range; otherwise None
        if len(self.voltage_ranges) == 0:
            self.voltage_range = None
        elif len(self.voltage_ranges) == 1:
            self.voltage_range = self.voltage_ranges[0]
        elif all(r == self.voltage_ranges[0] for r in self.voltage_ranges):
            self.voltage_range = self.voltage_ranges[0]
        else:
            self.voltage_range = None

        if len(self.temperature_ranges) == 0:
            self.temperature_range = None
        elif len(self.temperature_ranges) == 1:
            self.temperature_range = self.temperature_ranges[0]
        elif all(r == self.temperature_ranges[0] for r in self.temperature_ranges):
            self.temperature_range = self.temperature_ranges[0]
        else:
            self.temperature_range = None

def is_valid_voltage_range(start, end):
    """Validate voltage range is within reasonable bounds for electronic components"""
    MAX_VOLTAGE = 100
    MIN_VOLTAGE = -50
    
    if not (MIN_VOLTAGE <= start <= MAX_VOLTAGE and 
            MIN_VOLTAGE <= end <= MAX_VOLTAGE):
        return False
    if start > end:
        return False
    if abs(end - start) > MAX_VOLTAGE:
        return False
    if abs(end - start) < 0.1:
        return False
    return True

def parse_ranges(content, pattern):
    matches = pattern.findall(content)
    ranges = set()  # Use set to avoid duplicates
    
    # Extract numbers with their signs, whether from tuples or strings
    numbers_pattern = re.compile(r'[-+]?\s*\d+\.?\d*')
    
    # Split content into lines to handle multi-line matches better
    lines = content.split('\n')
    for line in lines:
        match_iter = pattern.finditer(line)
        for match in match_iter:
            match_text = match.group(0)
            numbers = numbers_pattern.findall(match_text)
            
            if len(numbers) >= 2:
                try:
                    start = float(numbers[0].replace(' ', ''))
                    end = float(numbers[1].replace(' ', ''))
                    
                    # Handle negative signs in context
                    if match_text.find(numbers[0]) > 0 and match_text[match_text.find(numbers[0])-1] == '-':
                        start = -start
                    if match_text.find(numbers[1]) > 0 and match_text[match_text.find(numbers[1])-1] == '-':
                        end = -end
                    
                    # Ensure start is less than end
                    if start > end:
                        start, end = end, start
                        
                    # For voltage ranges, apply additional validation
                    if pattern == voltage_pattern and not is_valid_voltage_range(start, end):
                        continue
                        
                    ranges.add((start, end))  # Add to set instead of list
                except (ValueError, IndexError):
                    continue
    
    return list(ranges)  # Convert back to list

def parse_component_file(filepath, verbose=False):
    component_name = os.path.basename(filepath)
    component = Component(component_name)

    try:
        with open(filepath, 'rb') as file:
            content_bytes = file.read()

        try:
            content = content_bytes.decode('latin-1')
        except UnicodeDecodeError:
            if verbose:
                logger.warning(f"Latin-1 decode failed for {filepath}, trying UTF-8")
            try:
                content = content_bytes.decode('utf-8')
            except UnicodeDecodeError:
                if verbose:
                    logger.error(f"Failed to decode {filepath} with both Latin-1 and UTF-8")
                return component

        component.voltage_ranges = parse_ranges(content, voltage_pattern)
        component.temperature_ranges = parse_ranges(content, temp_pattern)

        if verbose:
            logger.info(f"Component: {component.name}")
            logger.info(f"  Extracted voltage ranges: {component.voltage_ranges}")
            logger.info(f"  Extracted temperature ranges: {component.temperature_ranges}")

        component.determine_ranges()

        if verbose:
            logger.info(f"  Determined voltage range: {component.voltage_range}")
            logger.info(f"  Determined temperature range: {component.temperature_range}\n")

    except IOError as e:
        if verbose:
            logger.error(f"Error reading file {filepath}: {str(e)}")
    except Exception as e:
        if verbose:
            logger.error(f"Unexpected error processing {filepath}: {str(e)}")

    return component

def load_components(directory, verbose=False):
    if not os.path.exists(directory):
        logger.error(f"Directory not found: {directory}")
        return []
        
    components = []
    stats = {
        'total_files': 0,
        'multiple_ranges_rejected': 0,
        'invalid_ranges_rejected': 0,
        'successful_parse': 0
    }
    
    try:
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.txt'):
                    stats['total_files'] += 1
                    filepath = os.path.join(root, filename)
                    component = parse_component_file(filepath, verbose)
                    
                    if component.voltage_range is None and len(component.voltage_ranges) > 1:
                        stats['multiple_ranges_rejected'] += 1
                    elif component.voltage_range is None and len(component.voltage_ranges) == 0:
                        stats['invalid_ranges_rejected'] += 1
                    else:
                        stats['successful_parse'] += 1
                        
                    components.append(component)
    except Exception as e:
        logger.error(f"Error walking directory {directory}: {str(e)}")
    
    if verbose:
        logger.info("\nParsing Statistics:")
        logger.info(f"Total files processed: {stats['total_files']}")
        logger.info(f"Successfully parsed: {stats['successful_parse']}")
        logger.info(f"Rejected (multiple ranges): {stats['multiple_ranges_rejected']}")
        logger.info(f"Rejected (invalid ranges): {stats['invalid_ranges_rejected']}")
    
    return components

def find_compatible_components(components, voltage, temperature):
    if not isinstance(voltage, (int, float)) or not isinstance(temperature, (int, float)):
        raise ValueError("Voltage and temperature must be numeric values")
        
    compatible = []
    for component in components:
        v_range = component.voltage_range
        t_range = component.temperature_range

        if v_range and t_range:
            if v_range[0] <= voltage <= v_range[1] and t_range[0] <= temperature <= t_range[1]:
                compatible.append(component.name)
    return compatible

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Component Compatibility Checker')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.INFO)
        # Switch to more detailed format for verbose mode
        for handler in logger.handlers:
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    if not os.path.exists('Task example files'):
        logger.error("Component directory not found")
        exit(1)
        
    components = load_components('Task example files', verbose=args.verbose)
    
    if not components:
        logger.error("No components found in directory")
        exit(1)

    try:
        voltage = float(input("Enter operating voltage (V): "))
        temperature = float(input("Enter operating temperature (°C): "))
    except ValueError:
        logger.error("Invalid input. Please enter numeric values.")
        exit(1)

    compatible_components = find_compatible_components(components, voltage, temperature)

    if compatible_components:
        print("\nCompatible components:")
        for name in compatible_components:
            print(f"- {name}")
    else:
        print("\nNo compatible components found.") 