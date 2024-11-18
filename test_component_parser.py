#!/usr/bin/env python3

import os
import unittest
from component_parser import (
    Component, 
    find_compatible_components, 
    parse_ranges,
    voltage_pattern,
    temp_pattern,
    load_components
)

MAX_VOLTAGE = 100
MIN_VOLTAGE = -50

class TestComponent(unittest.TestCase):
    def test_determine_ranges_identical(self):
        comp = Component("TestComponent")
        comp.voltage_ranges = [(5.0, 12.0), (5.0, 12.0)]
        comp.temperature_ranges = [(-40.0, 85.0), (-40.0, 85.0)]
        comp.determine_ranges()
        self.assertEqual(comp.voltage_range, (5.0, 12.0))
        self.assertEqual(comp.temperature_range, (-40.0, 85.0))

    def test_determine_ranges_not_identical(self):
        comp = Component("TestComponent")
        comp.voltage_ranges = [(3.3, 5.0), (5.0, 12.0)]
        comp.temperature_ranges = [(-20.0, 70.0), (-40.0, 85.0)]
        comp.determine_ranges()
        self.assertIsNone(comp.voltage_range)
        self.assertIsNone(comp.temperature_range)

    def test_find_compatible_components(self):
        comp1 = Component("Comp1")
        comp1.voltage_range = (5.0, 12.0)
        comp1.temperature_range = (-40.0, 85.0)

        comp2 = Component("Comp2")
        comp2.voltage_range = None
        comp2.temperature_range = (-40.0, 85.0)

        components = [comp1, comp2]
        compatible = find_compatible_components(components, 5.0, 25.0)
        self.assertIn("Comp1", compatible)
        self.assertNotIn("Comp2", compatible)

        # Test boundaries
        self.assertIn("Comp1", find_compatible_components(components, 5.0, -40.0))
        self.assertIn("Comp1", find_compatible_components(components, 12.0, 85.0))
        self.assertEqual(len(find_compatible_components(components, 4.9, 25.0)), 0)

    def test_parse_ranges_with_different_formats(self):
        voltage_content = """
        VDD: 3.3V to 5V
        Input voltage: -12V to +12V
        Supply voltage, 1.8V - 3.6V
        """
        voltage_ranges = parse_ranges(voltage_content, voltage_pattern)
        self.assertEqual(len(voltage_ranges), 3)
        self.assertIn((-12.0, 12.0), voltage_ranges)

        temp_content = """
        Operating temperature: -40°C to +85°C
        Ta = -20C to 70C
        Temperature Range: -50°C to 0°C
        """
        temp_ranges = parse_ranges(temp_content, temp_pattern)
        self.assertEqual(len(temp_ranges), 3)
        self.assertIn((-40.0, 85.0), temp_ranges)
        self.assertIn((-50.0, 0.0), temp_ranges)

    def test_real_component_data(self):
        content = """
        Wide operating temperature: -40°C to +125°C
        Supply voltage: 1.71V to 5.5V
        """
        voltage_ranges = parse_ranges(content, voltage_pattern)
        temp_ranges = parse_ranges(content, temp_pattern)
        self.assertEqual(voltage_ranges, [(1.71, 5.5)])
        self.assertEqual(temp_ranges, [(-40.0, 125.0)])

    def test_invalid_inputs(self):
        components = [Component("test")]
        with self.assertRaises(ValueError):
            find_compatible_components(components, "invalid", 25.0)
        with self.assertRaises(ValueError):
            find_compatible_components(components, 5.0, "invalid")

    def test_component_directory(self):
        self.assertTrue(os.path.exists('Task example files'))
        components = load_components('Task example files')
        self.assertGreater(len(components), 0)

    def test_operation_suffix_format(self):
        """Test voltage ranges with 'Operation' suffix and no space before V"""
        content = """
        3.15V to 3.45V Operation
        4.2V to 5.5V operation
        VDD = 3.3V to 5.0V
        """
        voltage_ranges = parse_ranges(content, voltage_pattern)
        self.assertEqual(len(voltage_ranges), 3)
        self.assertIn((3.15, 3.45), voltage_ranges)  # Test Operation suffix
        self.assertIn((4.2, 5.5), voltage_ranges)    # Test operation suffix
        self.assertIn((3.3, 5.0), voltage_ranges)    # Test normal format

        # Test with real file content
        content = """Industrial Temperature Range: -40°C to +85°C with LOS
        3.15V to 3.45V Operation"""
        voltage_ranges = parse_ranges(content, voltage_pattern)
        self.assertEqual(len(voltage_ranges), 1)
        self.assertEqual(voltage_ranges[0], (3.15, 3.45))

if __name__ == '__main__':
    unittest.main() 