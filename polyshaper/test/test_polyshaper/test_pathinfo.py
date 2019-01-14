#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper path statistics test

NOTE: to run this test standalone you must add ../plugin to the PYTHONPATH shell
variable tro to sys.path as well as the global inkscape plugin directory. If run
through testAll.py, there is no need to add directories (they are inserted by
that script)
"""

from datetime import datetime
import math
import unittest
from polyshaper.pathinfo import PathInfo # pylint: disable=import-error,no-name-in-module

# The value of speed (mm/min) used in this test. This MUST be a float for tests to be correct
MM_PER_MIN = 17.0

class DummyOptions():
    """ A dummy class to store options
    """

    def __init__(self):
        self.dim_x = 50
        self.dim_y = 50
        self.speed = MM_PER_MIN

class PathInfoTest(unittest.TestCase):
    """ Tests the class computing path statistics
    """

    def test_return_inside_workpiece_for_empty_path(self): # pylint: disable=invalid-name
        """ Test that is_path_inside_workpiece returns true for empty paths
        """

        stats = PathInfo([], DummyOptions(), "baseF")
        self.assertTrue(stats.is_path_inside_workpiece())

    def test_return_outside_workpiece_when_path_top_outside(self): # pylint: disable=invalid-name
        """ Tests that when the path is outside border (top) is_path_inside_border returns false
        """

        path = [
            (0, 0),
            (10, 10),
            (5, 51),
            (15, 14),
            (11, 17),
            (0, 0)
        ]
        stats = PathInfo(path, DummyOptions(), "baseF")

        self.assertFalse(stats.is_path_inside_workpiece())

    def test_return_outside_workpiece_when_path_bottom_outside(self): # pylint: disable=invalid-name
        """ Tests that when the path is outside border (bottom) is_path_inside_border returns false
        """

        path = [
            (0, 0),
            (10, 10),
            (5, -1),
            (15, 14),
            (11, 17),
            (0, 0)
        ]
        stats = PathInfo(path, DummyOptions(), "baseF")

        self.assertFalse(stats.is_path_inside_workpiece())

    def test_return_outside_workpiece_when_path_left_outside(self): # pylint: disable=invalid-name
        """ Tests that when the path is outside border (left) is_path_inside_border returns false
        """

        path = [
            (0, 0),
            (10, 10),
            (-1, 20),
            (15, 14),
            (11, 17),
            (0, 0)
        ]
        stats = PathInfo(path, DummyOptions(), "baseF")

        self.assertFalse(stats.is_path_inside_workpiece())

    def test_return_outside_workpiece_when_path_right_outside(self): # pylint: disable=invalid-name
        """ Tests that when the path is outside border (right) is_path_inside_border returns false
        """

        path = [
            (0, 0),
            (10, 10),
            (51, 20),
            (15, 14),
            (11, 17),
            (0, 0)
        ]
        stats = PathInfo(path, DummyOptions(), "baseF")

        self.assertFalse(stats.is_path_inside_workpiece())

    def test_return_inside_border_when_path_inside(self): # pylint: disable=invalid-name
        """ Tests that when the path is inside border is_path_inside_border returns true
        """

        path = [
            (0, 0),
            (10, 10),
            (20, 20),
            (15, 14),
            (11, 17),
            (0, 0)
        ]
        ops = DummyOptions()
        ops.dim_x = 20
        ops.dim_y = 20
        stats = PathInfo(path, ops, "baseF")

        self.assertTrue(stats.is_path_inside_workpiece())

    def test_estimate_working_time_to_0_if_path_is_missing(self): # pylint: disable=invalid-name
        """ Tests that working time if estimated to 0 is path is missing
        """

        ops = DummyOptions()
        ops.dim_x = 12
        ops.dim_y = 34
        stats = PathInfo([], ops, "baseF")

        self.assertEqual(stats.working_time_min(), 0)

    def test_estimate_working_time_to_0_if_path_single_point(self): # pylint: disable=invalid-name
        """ Tests that working time is 0 if path contains a single point
        """

        ops = DummyOptions()
        ops.dim_x = 12
        ops.dim_y = 34
        stats = PathInfo([(1, 1)], ops, "baseF")

        self.assertEqual(stats.working_time_min(), 0)

    def test_estimate_working_time(self):
        """ Tests estimated working time for a path
        """

        path = [
            (0, 0),
            (10, 0),
            (10, 10),
            (0, 10)
        ]
        ops = DummyOptions()
        ops.dim_x = 12
        ops.dim_y = 34
        stats = PathInfo(path, ops, "baseF")

        self.assertEqual(stats.working_time_min(), int(math.ceil(30 / MM_PER_MIN)))

    def test_estimate_to_0_if_speed_is_0(self): # pylint: disable=invalid-name
        """ Tests that working time estimate is 0 if speed is 0
        """

        path = [
            (0, 0),
            (10, 0),
            (10, 10),
            (0, 10)
        ]
        ops = DummyOptions()
        ops.dim_x = 12
        ops.dim_y = 34
        ops.speed = 0
        stats = PathInfo(path, ops, "baseF")

        self.assertEqual(stats.working_time_min(), 0)

    def test_generate_gcode_filename(self):
        """ Tests that the generated gcode filename is correct
        """

        stats = PathInfo([], DummyOptions, "baseF")

        self.assertEqual(stats.gcode_filename(), "baseF.gcode")

    def test_generate_svg_filename(self):
        """ Tests that the generated svg filename is correct
        """

        stats = PathInfo([], DummyOptions, "baseF")

        self.assertEqual(stats.svg_filename(), "baseF.svg")

    def test_generate_metainfo_filename(self):
        """ Tests that the generated metainfo filename is correct
        """

        stats = PathInfo([], DummyOptions, "baseF")

        self.assertEqual(stats.metainfo_filename(), "baseF.psj")

    def test_generate_metainfo(self):
        """ Tests that meta-information is correctly generated
        """

        path = [
            (0, 0),
            (10, 0),
            (10, 10),
            (0, 10)
        ]
        ops = DummyOptions()
        ops.shapename = "uhuh"
        ops.dim_x = 12
        ops.dim_y = 34
        ops.speed = 15.0
        ops.flatness = 0.3
        ops.square = False
        ops.margin = 2.5
        ops.machine_type = "P400"
        ops.draw_toolpath = False
        ops.auto_close_path = True
        stats = PathInfo(path, ops, "baseF")

        metainfo = stats.metainfo()
        self.assertEqual(metainfo["version"], 1)
        self.assertEqual(metainfo["name"], "uhuh")
        self.assertEqual(metainfo["generatedBy"], "2DPlugin")
        self.assertEqual(metainfo["gcodeFilename"], "baseF.gcode")
        self.assertEqual(metainfo["svgFilename"], "baseF.svg")
        self.assertEqual(metainfo["duration"], 120)
        self.assertLess(abs((datetime.strptime(metainfo["creationTime"], "%Y-%m-%dT%H:%M:%S.%f") -
                             datetime.now()).total_seconds()), 1)
        self.assertEqual(metainfo["pointsInsideWorkpiece"], True)
        self.assertEqual(metainfo["speed"], 15.0)
        self.assertEqual(metainfo["flatness"], 0.3)
        self.assertEqual(metainfo["square"], False)
        self.assertEqual(metainfo["margin"], 2.5)
        self.assertEqual(metainfo["machineType"], "P400")
        self.assertEqual(metainfo["drawToolpath"], False)
        self.assertEqual(metainfo["autoClosePath"], True)
