#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper gcode generation tests

NOTE: to run this test standalone you must add ../plugin to the PYTHONPATH shell
variable tro to sys.path as well as the global inkscape plugin directory. If run
through testAll.py, there is no need to add directories (they are inserted by
that script)
"""

import unittest
import math
from polyshaper.gcode import EngravingGCodeGenerator, CuttingGCodeGenerator # pylint: disable=import-error,no-name-in-module

# The value of mm_per_degree used in this test
MM_PER_DEGREE = 18.0

def angle_to_e(angle):
    """ Converts an angle to an E value
    """

    return math.degrees(angle) / MM_PER_DEGREE

class EngravingGCodeGeneratorTest(unittest.TestCase):
    """ Tests the class generating the g-code for engraving
    """

    def test_no_paths_generate_no_gcode(self):
        """ Tests that when no paths are provided, no gcode is generated
        """

        generator = EngravingGCodeGenerator([], MM_PER_DEGREE, 10, 2, math.radians(30))
        generator.generate()

        self.assertEqual(generator.gcode(), None)

    def test_all_paths_empty_generate_no_gcode(self): # pylint: disable=invalid-name
        """ Tests that when empty paths are provided, no gcode is generated
        """

        generator = EngravingGCodeGenerator([[], [], []], MM_PER_DEGREE, 10, 2, math.radians(30))
        generator.generate()

        self.assertEqual(generator.gcode(), None)

    def test_single_path_with_single_point(self): # pylint: disable=invalid-name
        """ Tests that the generated gcode for a path made up of a single point is the expected one
        """

        generator = EngravingGCodeGenerator([[(1, 2, 3, 0)]], MM_PER_DEGREE, 17, 2,
                                            math.radians(30))
        generator.generate()

        expected_gcode = ("M3\n" +
                          "G01 F300\n" +
                          "G00 Z17.000\n" +
                          "G00 X1.000 Y2.000 E0.000\n" +
                          "G01 Z3.000\n" +
                          "G01 Z17.000\n" +
                          "G00 X0.000 Y0.000 E0.000\n" +
                          "G00 Z0.000\n" +
                          "M5\n")

        self.assertEqual(generator.gcode(), expected_gcode)

    def test_single_path_with_multiple_points(self): # pylint: disable=invalid-name
        """ Tests that the generated gcode for a path with multiple points is the expected one

        Here points are distant from each other, so the resulting gcode first rotates the tool, then
        moves it
        """

        generator = EngravingGCodeGenerator([[
            (100, 200, 300, 0.3),
            (1000, 2000, 3200, 1.5),
            (4500, 3300, 8700, 1.2),
            (6400, 7700, 6200, 2.5),
            (0, 3200, 4400, 0)]], MM_PER_DEGREE, 57, 2, math.radians(30))
        generator.generate()

        expected_gcode = ("M3\n" +
                          "G01 F300\n" +
                          "G00 Z57.000\n" +
                          "G00 X100.000 Y200.000 E{:5.3f}\n".format(angle_to_e(0.3)) +
                          "G01 Z300.000\n" +
                          "G01 X1000.000 Y2000.000 Z3200.000\n" +
                          "G01 E{:5.3f}\n".format(angle_to_e(1.5)) +
                          "G01 X4500.000 Y3300.000 Z8700.000\n" +
                          "G01 E{:5.3f}\n".format(angle_to_e(1.2)) +
                          "G01 X6400.000 Y7700.000 Z6200.000\n" +
                          "G01 E{:5.3f}\n".format(angle_to_e(2.5)) +
                          "G01 X0.000 Y3200.000 Z4400.000\n" +
                          "G01 E{:5.3f}\n".format(angle_to_e(0)) +
                          "G01 Z57.000\n" +
                          "G00 X0.000 Y0.000 E0.000\n" +
                          "G00 Z0.000\n" +
                          "M5\n")

        self.assertEqual(generator.gcode(), expected_gcode)

    def test_multiple_paths_with_multiple_points(self): # pylint: disable=invalid-name
        """ Tests that the generated gcode for multiple paths with multiple points is correct

        Here points are distant from each other, so the resulting gcode first rotates the tool, then
        moves it
        """

        generator = EngravingGCodeGenerator([
            [(100, 200, 300, 0.3),
             (1000, 2000, 3200, 1.5),
             (500, 500, 500, 0)],
            [(4500, 3300, 8700, 1.2),
             (6400, 7700, 6200, 2.5),
             (0, 3200, 4400, 0)]], MM_PER_DEGREE, 33, 2, math.radians(30))
        generator.generate()

        expected_gcode = ("M3\n" +
                          "G01 F300\n" +
                          "G00 Z33.000\n" +
                          "G00 X100.000 Y200.000 E{:5.3f}\n".format(angle_to_e(0.3)) +
                          "G01 Z300.000\n" +
                          "G01 X1000.000 Y2000.000 Z3200.000\n" +
                          "G01 E{:5.3f}\n".format(angle_to_e(1.5)) +
                          "G01 X500.000 Y500.000 Z500.000\n" +
                          "G01 E{:5.3f}\n".format(angle_to_e(0)) +
                          "G01 Z33.000\n" +
                          "G00 X4500.000 Y3300.000 E{:5.3f}\n".format(angle_to_e(1.2)) +
                          "G01 Z8700.000\n" +
                          "G01 X6400.000 Y7700.000 Z6200.000\n" +
                          "G01 E{:5.3f}\n".format(angle_to_e(2.5)) +
                          "G01 X0.000 Y3200.000 Z4400.000\n" +
                          "G01 E{:5.3f}\n".format(angle_to_e(0)) +
                          "G01 Z33.000\n" +
                          "G00 X0.000 Y0.000 E0.000\n" +
                          "G00 Z0.000\n" +
                          "M5\n")

        self.assertEqual(generator.gcode(), expected_gcode)

    def test_path_with_near_points_and_angle(self): # pylint: disable=invalid-name
        """ Tests gcode generation for points at a low distance and low angular displacement
        """

        generator = EngravingGCodeGenerator([[
            (100, 200, 300, 0.3),
            (110, 200, 300, 0.5),
            (105, 205, 300, 1.2),
            (106, 206, 300, 1.3),
            (200, 100, 300, 1.3),
            (0, 0, 300, 0)]], MM_PER_DEGREE, 57, 20, 0.5)
        generator.generate()

        expected_gcode = ("M3\n" +
                          "G01 F300\n" +
                          "G00 Z57.000\n" +
                          "G00 X100.000 Y200.000 E{:5.3f}\n".format(angle_to_e(0.3)) +
                          "G01 Z300.000\n" +
                          "G01 X110.000 Y200.000 Z300.000 E{:5.3f}\n".format(angle_to_e(0.5)) +
                          "G01 X105.000 Y205.000 Z300.000\n" +
                          "G01 E{:5.3f}\n".format(angle_to_e(1.2)) +
                          "G01 X106.000 Y206.000 Z300.000 E{:5.3f}\n".format(angle_to_e(1.3)) +
                          "G01 X200.000 Y100.000 Z300.000\n" +
                          "G01 E{:5.3f}\n".format(angle_to_e(1.3)) +
                          "G01 X0.000 Y0.000 Z300.000\n" +
                          "G01 E{:5.3f}\n".format(angle_to_e(0)) +
                          "G01 Z57.000\n" +
                          "G00 X0.000 Y0.000 E0.000\n" +
                          "G00 Z0.000\n" +
                          "M5\n")

        self.assertEqual(generator.gcode(), expected_gcode)


# The value of speed used in this test
SPEED = 313

class CuttingGCodeGeneratorTest(unittest.TestCase):
    """ Tests the class generating the g-code for engraving
    """

    def test_empty_path_generate_no_gcode(self): # pylint: disable=invalid-name
        """ Tests that when an empty path is provided, no gcode is generated
        """

        generator = CuttingGCodeGenerator([], SPEED)
        generator.generate()

        self.assertEqual(generator.gcode(), None)

    def test_path_with_single_point(self): # pylint: disable=invalid-name
        """ Tests that the generated gcode for a path made up of a single point is the expected one
        """

        generator = CuttingGCodeGenerator([(1, 2)], SPEED)
        generator.generate()

        expected_gcode = ("M3\n" +
                          "G01 F313.000\n" +
                          "G01 X1.000 Y2.000\n" +
                          "M5\n")

        self.assertEqual(generator.gcode(), expected_gcode)

    def test_path_with_multiple_points(self): # pylint: disable=invalid-name
        """ Tests that the generated gcode for a path made up of multiple points is the expected one
        """

        generator = CuttingGCodeGenerator([(1, 2), (3, 4), (5, 6), (7, 8), (9, 0)], SPEED)
        generator.generate()

        expected_gcode = ("M3\n" +
                          "G01 F313.000\n" +
                          "G01 X1.000 Y2.000\n" +
                          "G01 X3.000 Y4.000\n" +
                          "G01 X5.000 Y6.000\n" +
                          "G01 X7.000 Y8.000\n" +
                          "G01 X9.000 Y0.000\n" +
                          "M5\n")

        self.assertEqual(generator.gcode(), expected_gcode)
